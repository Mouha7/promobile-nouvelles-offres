"""Génère assets/og-image.png (1200 × 630) : l'aperçu affiché quand le lien est
partagé sur WhatsApp, Facebook ou LinkedIn. Lit offres.js pour la date et les gains.

Usage : python3 tools/build_og_image.py
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from offres_data import RACINE, charger  # noqa: E402

ROUGE = (227, 6, 19)
BLANC = (255, 255, 255)


def police(poids: str, taille: int) -> ImageFont.FreeTypeFont:
    """FreeType lit le WOFF (pas le WOFF2) : on convertit à la volée via fontTools."""
    cache = RACINE / "tools" / ".fonts"
    cache.mkdir(exist_ok=True)
    ttf = cache / f"poppins-{poids}.ttf"
    if not ttf.exists():
        from fontTools.ttLib import TTFont
        f = TTFont(RACINE / "assets" / "fonts" / f"poppins-latin-{poids}-normal.woff2")
        f.flavor = None
        f.save(ttf)
    return ImageFont.truetype(str(ttf), taille)


def main() -> None:
    d = charger()
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), ROUGE)
    dr = ImageDraw.Draw(im)

    # Grand « + » décoratif en filigrane, à droite
    plus = police("700", 760)
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(calque).text((860, -200), "+", font=plus, fill=(255, 255, 255, 26))
    im.paste(calque, (0, 0), calque)
    dr = ImageDraw.Draw(im)

    # Logo sur cartouche blanc
    logo = Image.open(RACINE / "assets" / "logo-promobile.png").convert("RGBA")
    lw = 300
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    pad = 18
    dr.rounded_rectangle((70, 60, 70 + lw + 2 * pad, 60 + logo.height + 2 * pad), radius=18, fill=BLANC)
    im.paste(logo, (70 + pad, 60 + pad), logo)
    dr = ImageDraw.Draw(im)

    # Pastille date
    f_chip = police("600", 26)
    chip = f"Nouvelles offres · dès le {d['lancementTexte']}"
    tw = dr.textlength(chip, font=f_chip)
    cx, cy = 70, 200
    dr.rounded_rectangle((cx, cy, cx + tw + 44, cy + 50), radius=25, outline=(255, 255, 255), width=2, fill=None)
    dr.text((cx + 22, cy + 9), chip, font=f_chip, fill=BLANC)

    # Slogan sur deux lignes
    f_h1 = police("700", 92)
    dr.text((64, 270), "Plus de valeur,", font=f_h1, fill=BLANC)
    dr.text((64, 372), "au même prix.", font=f_h1, fill=BLANC)

    # Rangée des gains
    f_g = police("600", 30)
    gains = []
    for o in d["offres"]:
        g = o["gain"]
        if g not in gains:
            gains.append(g)
    x, y = 70, 520
    for g in gains:
        tw = dr.textlength(g, font=f_g)
        if x + tw + 36 > W - 60:
            break
        dr.rounded_rectangle((x, y, x + tw + 36, y + 56), radius=28, fill=(255, 255, 255))
        dr.text((x + 18, y + 10), g, font=f_g, fill=ROUGE)
        x += tw + 36 + 14

    sortie = RACINE / "assets" / "og-image.png"
    im.save(sortie, optimize=True)
    print(f"OK {sortie.relative_to(RACINE)} — {sortie.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
