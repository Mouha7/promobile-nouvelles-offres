"""Lecture de offres.js (source unique de vérité) depuis Python.

Le fichier est du JavaScript, mais tout ce qui suit « var PROMOBILE = »
est du JSON strict : on l'extrait et on le parse. Importé par
build_catalogue.py et build_og_image.py.
"""
from __future__ import annotations

import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent


def charger(chemin: pathlib.Path | None = None) -> dict:
    chemin = chemin or RACINE / "offres.js"
    texte = chemin.read_text(encoding="utf-8")
    debut = texte.index("PROMOBILE")
    debut = texte.index("{", debut)
    fin = texte.rindex("}") + 1
    return json.loads(texte[debut:fin])


def fcfa(n: int) -> str:
    """1375 -> « 1 375 » (espace fine insécable, comme sur la page)."""
    return f"{n:,}".replace(",", " ")


if __name__ == "__main__":
    d = charger()
    print(f"{len(d['offres'])} offres — lancement {d['lancementTexte']} — WhatsApp {d['whatsapp']}")
    for o in d["offres"]:
        print(f"  {o['nom']:<20} {o['gain']:<10} {fcfa(o['prix']):>6} F  {o['validiteLongue']}")
