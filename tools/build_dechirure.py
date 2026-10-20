"""Déchirure du héros : la fissure suit la frontière du Sénégal (easter egg).

La page se fissure exactement selon la frontière (Natural Earth 1:10m, domaine public, tools/data/senegal.geojson) ;
la pièce de papier « Sénégal » est éjectée et laisse un trou rouge en forme de pays (la Gambie reste en papier),
puis les lambeaux, évidés de cette forme, s'ouvrent autour de la carte.

Ce module produit la zone <!-- gen:papier --> d'index.html (appelé par build_page.py) :
  --sn   : la frontière, en polygon() relatif à la boîte du papier (rapport largeur/hauteur BOITE) ;
  --hors : la boîte moins le Sénégal (evenodd), la découpe des lambeaux ;
  le tracé SVG de la fissure (c0) et le masque des autres fissures (hors du Sénégal).
Les lambeaux et les fissures radiales sont calculés dans <head> (graine fixe), comme avant.

Usage seul : python3 tools/build_dechirure.py   → affiche le nombre de sommets et l'emprise.
"""
from __future__ import annotations

import json
import math
import pathlib

ICI = pathlib.Path(__file__).resolve().parent
DONNEES = ICI / "data" / "senegal.geojson"
BOITE = 1.82        # rapport largeur / hauteur de la boîte du papier (CSS : .papier{aspect-ratio:1.82})
HAUT = 0.84         # le Sénégal occupe 84 % de la hauteur de la boîte, centré, sans déformation
LAT0 = 14.5         # projection équirectangulaire : x = lon · cos(14,5°)
TOLERANCE = 0.03   # Douglas–Peucker, en degrés projetés (~ 170 sommets)


def _dp(p: list, tol: float) -> list:
    if len(p) < 3:
        return p
    (ax, ay), (bx, by) = p[0], p[-1]
    dx, dy = bx - ax, by - ay
    long_ = math.hypot(dx, dy) or 1e-12
    dmax, imax = -1.0, 0
    for i in range(1, len(p) - 1):
        d = abs(dy * p[i][0] - dx * p[i][1] + bx * ay - by * ax) / long_
        if d > dmax:
            dmax, imax = d, i
    if dmax > tol:
        return _dp(p[:imax + 1], tol)[:-1] + _dp(p[imax:], tol)
    return [p[0], p[-1]]


def contour() -> list[tuple[float, float]]:
    """Frontière simplifiée, en % de la boîte du papier, en partant du Cap-Vert (point le plus à l'ouest)."""
    anneau = json.loads(DONNEES.read_text(encoding="utf-8"))["geometry"]["coordinates"][0]
    k = math.cos(math.radians(LAT0))
    pts = [(lon * k, -lat) for lon, lat in anneau]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    o = min(range(len(pts)), key=lambda i: pts[i][0])
    pts = pts[o:] + pts[:o]
    e = max(range(len(pts)), key=lambda i: pts[i][0])
    s = _dp(pts[:e + 1], TOLERANCE)[:-1] + _dp(pts[e:] + [pts[0]], TOLERANCE)[:-1]
    xs, ys = [p[0] for p in s], [p[1] for p in s]
    x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    larg = HAUT * (w / h) / BOITE                       # largeur occupée, en fraction de la boîte
    return [((0.5 - larg / 2 + (x - x0) / w * larg) * 100, (0.5 - HAUT / 2 + (y - y0) / h * HAUT) * 100) for x, y in s]


def _pc(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".") if "." in f"{v:.1f}" else f"{v:.1f}"


def html_papier() -> str:
    s = contour()
    sn = ",".join(f"{_pc(x)}% {_pc(y)}%" for x, y in s)
    d = "M" + "L".join(f"{_pc(x)} {_pc(y)}" for x, y in s) + "Z"
    # la frontière a son propre SVG au rapport de la boîte (182 × 100) : trait proportionnel, tracé par pathLength
    d182 = "M" + "L".join(f"{_pc(x * BOITE)} {_pc(y)}" for x, y in s) + "Z"
    pans = "".join(f'<div class="pan {n}"><i class="ombre"></i><i class="face"></i><i class="ton"></i></div>'
                   for n in ("pb1", "pb2", "pg", "pd", "ph2", "ph1"))
    return (f'<div class="papier" aria-hidden="true" style="--sn:polygon({sn});'
            f'--hors:polygon(evenodd,0 0,100% 0,100% 100%,0 100%,0 0,{sn},{_pc(s[0][0])}% {_pc(s[0][1])}%)">'
            f'<i class="cadre"></i>{pans}<i class="piece"><i class="face"></i><i class="ton"></i></i>'
            f'<svg class="fentes" viewBox="0 0 100 100" preserveAspectRatio="none" focusable="false">'
            f'<defs><clipPath id="hors-sn"><path clip-rule="evenodd" d="M0 0H100V100H0Z{d}"/></clipPath></defs>'
            f'<g clip-path="url(#hors-sn)"><path class="c1"/><path class="c2"/><path class="c3"/></g></svg>'
            f'<svg class="frontiere" viewBox="0 0 {_pc(100 * BOITE)} 100" preserveAspectRatio="none" focusable="false">'
            f'<path pathLength="1" d="{d182}"/></svg></div>')


if __name__ == "__main__":
    c = contour()
    xs, ys = [p[0] for p in c], [p[1] for p in c]
    print(f"{len(c)} sommets ; emprise x {min(xs):.1f}–{max(xs):.1f} %, y {min(ys):.1f}–{max(ys):.1f} % ; "
          f"html {len(html_papier())} caractères")
