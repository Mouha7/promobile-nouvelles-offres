"""Construit dist/apercu.html : la version « aperçu » publiée comme artifact Claude.

L'hébergeur d'aperçu enveloppe lui-même la page (doctype, <head>, <body>) et
n'autorise que les ressources inclues : on retire l'enveloppe et on inline les
polices et les images (data URI). Les données d'offres sont déjà inline (gen:donnees).
Le site réel (index.html) est d'abord régénéré par build_page.py, puis lu tel quel.

Usage : python3 tools/build_apercu.py
"""
from __future__ import annotations

import base64
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SRC = RACINE / "index.html"
DIST = RACINE / "dist"


def data_uri(chemin: str, type_mime: str) -> str:
    b64 = base64.b64encode((RACINE / chemin).read_bytes()).decode("ascii")
    return f"data:{type_mime};base64,{b64}"


def main() -> int:
    # 0. Page à jour avec offres.js
    if subprocess.run([sys.executable, str(RACINE / "tools" / "build_page.py")]).returncode:
        return 1
    html = SRC.read_text(encoding="utf-8")

    # 1. Contenu du <head> (sans charset/viewport, fournis par l'enveloppe) + contenu du <body>
    m_head = re.search(r"<head>(.*?)</head>", html, re.S)
    m_body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S)
    if not (m_head and m_body):
        print("ERREUR : <head> ou <body> introuvable dans index.html", file=sys.stderr)
        return 1
    head, body = m_head.group(1), m_body.group(1)
    head = re.sub(r"<meta charset=[^>]+>\s*", "", head)
    head = re.sub(r"<meta name=\"viewport\"[^>]+>\s*", "", head)
    head = re.sub(r"<link rel=\"preload\"[^>]+>\s*", "", head)
    if "<title>" not in head:
        print("ERREUR : <title> introuvable (zone gen:meta vide ?)", file=sys.stderr)
        return 1
    head = head.replace("<title>", "<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n<title>", 1)

    # 2. Polices et images en data URI
    head, n = re.subn(r'url\("(assets/fonts/[^"]+\.woff2)"\) format\("woff2"\)',
                      lambda m: f'url("{data_uri(m.group(1), "font/woff2")}") format("woff2")', head)
    if n == 0:
        print("ERREUR : aucune police trouvée à inliner", file=sys.stderr)
        return 1

    def image(m: re.Match) -> str:
        return f'{m.group(1)}="{data_uri(m.group(2), "image/png")}"'
    head = re.sub(r'(href|src)="(assets/[^"]+\.png)"', image, head)
    body = re.sub(r'(href|src)="(assets/[^"]+\.png)"', image, body)

    DIST.mkdir(exist_ok=True)
    sortie = DIST / "apercu.html"
    sortie.write_text(head.strip() + "\n" + body.strip() + "\n", encoding="utf-8")
    print(f"OK {sortie.relative_to(RACINE)} — {sortie.stat().st_size / 1024:.0f} Ko")
    return 0


if __name__ == "__main__":
    sys.exit(main())
