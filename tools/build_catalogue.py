"""Génère Catalogue_Offres_Promobile.pdf à partir de offres.js.

Usage :  python3 tools/build_catalogue.py
Sortie :  Catalogue_Offres_Promobile.pdf (à la racine, < 2 Mo — en pratique ~60 Ko)

Ce PDF est la version « générée » du catalogue : même données que la page.
Si l'équipe Marketing fournit son propre PDF, il suffit de remplacer le fichier
à la racine (même nom) — la page n'a pas besoin d'être modifiée.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, KeepTogether)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from offres_data import RACINE, charger, fcfa  # noqa: E402

ROUGE = colors.HexColor("#E30613")
ROUGE_PALE = colors.HexColor("#FDECEC")
NOIR = colors.HexColor("#212529")
GRIS = colors.HexColor("#5F646B")
LIGNE = colors.HexColor("#E8E3E3")
FOND2 = colors.HexColor("#F8F5F5")


def polices() -> tuple[str, str]:
    """Poppins si disponible (convertie depuis les woff2 du site), sinon Helvetica."""
    try:
        from fontTools.ttLib import TTFont as FTFont
        cache = RACINE / "tools" / ".fonts"
        cache.mkdir(exist_ok=True)
        for poids in ("400", "700"):
            ttf = cache / f"poppins-{poids}.ttf"
            if not ttf.exists():
                f = FTFont(RACINE / "assets" / "fonts" / f"poppins-latin-{poids}-normal.woff2")
                f.flavor = None
                f.save(ttf)
        pdfmetrics.registerFont(TTFont("Poppins", str(cache / "poppins-400.ttf")))
        pdfmetrics.registerFont(TTFont("Poppins-Bold", str(cache / "poppins-700.ttf")))
        pdfmetrics.registerFontFamily("Poppins", normal="Poppins", bold="Poppins-Bold",
                                      italic="Poppins", boldItalic="Poppins-Bold")
        return "Poppins", "Poppins-Bold"
    except Exception as exc:  # pragma: no cover - repli
        print("Poppins indisponible, repli Helvetica :", exc)
        return "Helvetica", "Helvetica-Bold"


def construire(sortie: pathlib.Path) -> None:
    d = charger()
    reg, gras = polices()
    date = dt.date.today().strftime("%d/%m/%Y")

    st = {
        "titre": ParagraphStyle("titre", fontName=gras, fontSize=24, leading=28, textColor=colors.white),
        "sous": ParagraphStyle("sous", fontName=reg, fontSize=11.5, leading=15, textColor=colors.white),
        "h2": ParagraphStyle("h2", fontName=gras, fontSize=15, leading=19, textColor=NOIR, spaceBefore=6, spaceAfter=6),
        "p": ParagraphStyle("p", fontName=reg, fontSize=9.8, leading=14, textColor=NOIR),
        "pg": ParagraphStyle("pg", fontName=reg, fontSize=9, leading=13, textColor=GRIS),
        "cell": ParagraphStyle("cell", fontName=reg, fontSize=8.8, leading=11.5, textColor=NOIR),
        "cellg": ParagraphStyle("cellg", fontName=reg, fontSize=8.8, leading=11.5, textColor=GRIS),
        "cellb": ParagraphStyle("cellb", fontName=gras, fontSize=8.8, leading=11.5, textColor=NOIR),
        "gain": ParagraphStyle("gain", fontName=gras, fontSize=11, leading=13, textColor=ROUGE),
        "ent": ParagraphStyle("ent", fontName=gras, fontSize=8.2, leading=10, textColor=colors.white),
        "code": ParagraphStyle("code", fontName=gras, fontSize=17, leading=21, textColor=ROUGE, alignment=TA_CENTER),
        "legal": ParagraphStyle("legal", fontName=reg, fontSize=7.4, leading=10, textColor=GRIS),
    }

    doc = SimpleDocTemplate(str(sortie), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm,
                            title="Catalogue des offres Promobile", author="Promobile — Sirius Télécoms Afrique SAU",
                            subject=d["slogan"], creator="build_catalogue.py")
    largeur = A4[0] - doc.leftMargin - doc.rightMargin
    corps = []

    # --- Bandeau rouge d'en-tête (logo sur cartouche blanc + titre) ---
    logo_path = RACINE / "assets" / "logo-promobile.png"
    logo = Image(str(logo_path), width=42 * mm, height=42 * mm * 174 / 640)
    cartouche = Table([[logo]], colWidths=[50 * mm], rowHeights=[16 * mm])
    cartouche.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    texte = [Paragraph("Catalogue des offres", st["titre"]), Spacer(1, 3),
             Paragraph(f"<b>{d['slogan']}</b> — nouvelles offres dès le {d['lancementTexte']}", st["sous"])]
    bandeau = Table([[cartouche, texte]], colWidths=[56 * mm, largeur - 56 * mm])
    bandeau.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ROUGE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 6 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 6 * mm),
        ("ROUNDEDCORNERS", [10, 10, 10, 10]),
    ]))
    corps += [bandeau, Spacer(1, 5 * mm)]

    corps.append(Paragraph(
        "Huit offres ProMINI, ProNET et ProMIX gagnent des Go, des minutes ou du bonus. "
        "Le prix et la validité ne changent pas. Les prix sont en francs CFA, toutes taxes comprises.",
        st["p"]))
    corps.append(Spacer(1, 3 * mm))

    # --- Tableau des 8 offres ---
    corps.append(Paragraph("Les 8 offres améliorées", st["h2"]))
    lignes = [[Paragraph(x, st["ent"]) for x in ("Offre", "Avant", "Après", "Prix", "Validité", "Gain")]]
    for o in d["offres"]:
        avant = "<br/>".join(f"{x['label']} : {x['avant']}" for x in o["details"])
        apres = "<br/>".join(
            (f"{x['label']} : <b><font color='#E30613'>{x['apres']}</font></b>" if x["change"]
             else f"{x['label']} : {x['apres']}") for x in o["details"])
        gain = o["gain"] + (f"<br/><font size='8.5'>{o['gainSecondaire']}</font>" if o.get("gainSecondaire") else "")
        lignes.append([
            Paragraph(f"<b>{o['nom']}</b><br/><font color='#5F646B' size='7.6'>{d['familles'][o['famille']]['libelle']}</font>"
                      f"<br/><font color='#E30613' size='9'><b>{o['code']}</b></font>", st["cell"]),
            Paragraph(avant, st["cellg"]), Paragraph(apres, st["cell"]),
            Paragraph(f"{fcfa(o['prix'])} F", st["cellb"]), Paragraph(o["validiteLongue"], st["cell"]),
            Paragraph(gain, st["gain"]),
        ])
    cw = [34 * mm, 40 * mm, 46 * mm, 18 * mm, 20 * mm, largeur - 158 * mm]
    t = Table(lignes, colWidths=cw, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NOIR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.6, LIGNE),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (5, 1), (5, -1), ROUGE_PALE),
    ]
    for i in range(1, len(lignes)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (4, i), FOND2))
    t.setStyle(TableStyle(style))
    corps += [t, Spacer(1, 5 * mm)]

    # --- Comment activer ---
    num = d["whatsapp"]
    affiche = num[3:] if num.startswith("221") else num
    affiche = " ".join([affiche[0:2], affiche[2:5], affiche[5:7], affiche[7:9]]) if len(affiche) == 9 else affiche
    bloc_ussd = [Paragraph("<b>Par le code</b>", st["p"]), Spacer(1, 2),
                 Paragraph(d["ussd"], st["code"]), Spacer(1, 2),
                 Paragraph("Composez le code de l'offre (en rouge dans le tableau) : elle s'active directement. "
                           f"Ou composez {d['ussd']} et suivez le menu.", st["pg"])]
    bloc_wa = [Paragraph("<b>Sur WhatsApp</b>", st["p"]), Spacer(1, 2),
               Paragraph(f"+221 {affiche}", st["code"]), Spacer(1, 2),
               Paragraph("Écrivez le nom de l'offre souhaitée, par exemple « Je souhaite activer l'offre ProNET 3 Go ».", st["pg"])]
    bloc_sc = [Paragraph("<b>Service client</b>", st["p"]), Spacer(1, 2),
               Paragraph(d["serviceClient"], st["code"]), Spacer(1, 2),
               Paragraph(f"Appel depuis votre ligne Promobile, ou {d['email']}.", st["pg"])]
    col = (largeur - 8 * mm) / 3
    tri = Table([[bloc_ussd, bloc_wa, bloc_sc]], colWidths=[col, col, col], hAlign="LEFT", spaceBefore=0)
    tri.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.8, LIGNE), ("BOX", (1, 0), (1, 0), 0.8, LIGNE), ("BOX", (2, 0), (2, 0), 0.8, LIGNE),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    corps.append(KeepTogether([Paragraph("Comment activer une offre", st["h2"]), tri]))
    corps.append(Spacer(1, 5 * mm))

    # --- Mentions ---
    corps.append(Paragraph(
        "Offres valables au Sénégal pour les clients Promobile, dans la limite des conditions générales disponibles sur "
        f"<a href='{d['siteOfficiel']}' color='#E30613'>promobile.sn</a>. Aucun paiement n'est demandé en dehors de votre crédit Promobile. "
        f"Document généré le {date} à partir des données officielles des offres — version {d['lancement']}. "
        "© 2026 Sirius Télécoms Afrique SAU. Tous droits réservés.", st["legal"]))

    def pied(canvas, doc_):
        canvas.saveState()
        canvas.setFillColor(ROUGE)
        canvas.rect(0, 0, A4[0], 3 * mm, stroke=0, fill=1)
        canvas.setFont(reg, 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(doc.leftMargin, 6 * mm, f"Promobile — {d['slogan']} — {d['ussd']}")
        canvas.drawRightString(A4[0] - doc.rightMargin, 6 * mm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(corps, onFirstPage=pied, onLaterPages=pied)
    taille = sortie.stat().st_size
    print(f"OK {sortie.name} — {taille / 1024:.0f} Ko")
    if taille > 2 * 1024 * 1024:
        raise SystemExit("Le PDF dépasse 2 Mo : à alléger (cahier des charges, F4).")


if __name__ == "__main__":
    construire(RACINE / charger()["catalogue"]["fichier"])
