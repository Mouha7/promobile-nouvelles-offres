"""Génère les parties de index.html qui dépendent de offres.js (source unique de vérité).

index.html sert à la fois de gabarit et de résultat : seules les zones balisées
<!-- gen:NOM --> … <!-- /gen:NOM --> et les petits textes <… data-d="clé">…</…>
du <body> sont réécrits ; tout le reste (design, CSS, JS) se modifie à la main.

Usage :
  python3 tools/build_page.py               met à jour index.html
  python3 tools/build_page.py --check       code 1 si index.html n'est pas à jour
  python3 tools/build_page.py --site _site  + dossier publiable (sitemap, robots, 404)

Bibliothèque standard uniquement : tourne tel quel dans la GitHub Action.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from offres_data import RACINE, charger  # noqa: E402

PAGE = RACINE / "index.html"
NBSP = " "


class Erreur(Exception):
    """Donnée de offres.js inutilisable : le build s'arrête avec un message clair."""


def e(texte: object) -> str:
    return html.escape(str(texte), quote=True)


def fcfa(n: int) -> str:
    """1375 -> « 1 375 » avec espace insécable U+00A0, comme le reste de la page."""
    return f"{n:,}".replace(",", NBSP)


def avertir(msg: str) -> None:
    prefixe = "::warning::" if os.environ.get("GITHUB_ACTIONS") else "ATTENTION : "
    print(prefixe + msg, file=sys.stderr)


# ---------------------------------------------------------------- lecture des valeurs

NOMBRE = re.compile(r"\s*(\d{1,3}(?:\s\d{3})+|\d+)(?:,(\d+))?\s*(Go|Mo|min|F|SMS)?(?:\s.*)?")


def valeur(texte: str, ou: str) -> tuple[float, str]:
    """« 2,5 Go » -> (2.5, "Go") ; « 2 000 F tous réseaux » -> (2000.0, "F") ; « 50 » -> (50.0, "")."""
    m = NOMBRE.fullmatch(texte)
    if not m:
        raise Erreur(f"{ou} : « {texte} » n'est pas une valeur lisible "
                     "(exemples valides : « 2,5 Go », « 1 000 F », « 80 min », « 50 »)")
    entier = re.sub(r"\s", "", m.group(1))
    nombre = float(entier + ("." + m.group(2) if m.group(2) else ""))
    return nombre, m.group(3) or ""


def jauges(o: dict) -> list[dict]:
    """Une jauge par ligne qui change : proportion ancien / nouveau."""
    sortie = []
    for d in o["details"]:
        if not d.get("change"):
            continue
        ou = f"offre « {o['nom']} », ligne « {d['label']} »"
        av, u1 = valeur(d["avant"], ou + " (avant)")
        ap, u2 = valeur(d["apres"], ou + " (après)")
        if u1 != u2:
            raise Erreur(f"{ou} : unités différentes avant/après (« {d['avant']} » / « {d['apres']} »)")
        if not 0 < av < ap:
            raise Erreur(f"{ou} : la valeur après doit être plus grande que la valeur avant")
        sortie.append({"label": d["label"], "avant": d["avant"], "apres": d["apres"],
                       "av": av, "ap": ap, "unite": u1, "r": av / ap})
    if not sortie:
        raise Erreur(f"offre « {o['nom']} » : aucune ligne « change: true » — rien à montrer en avant/après")
    return sortie


def verifier_gain(o: dict, js: list[dict]) -> None:
    """Simple avertissement si le gain saisi à la main ne correspond pas aux lignes avant/après."""
    for g in filter(None, [o.get("gain"), o.get("gainSecondaire")]):
        m = re.fullmatch(r"\+\s*(\d+(?:,\d+)?)\s*(Go|Mo|min|SMS|F)", g)
        if m:
            diff, unite = float(m.group(1).replace(",", ".")), m.group(2)
            ok = any(abs((j["ap"] - j["av"]) - diff) < 1e-9
                     and (j["unite"] == unite or (unite == "SMS" and j["label"] == "SMS")) for j in js)
        elif (m := re.search(r"×\s*(\d+)", g)):
            ok = any(abs(j["ap"] / j["av"] - int(m.group(1))) < 1e-9 for j in js)
        else:
            ok = True
        if not ok:
            avertir(f"offre « {o['nom']} » : le gain « {g} » ne correspond à aucune ligne avant/après")


def duree(o: dict) -> tuple[int, str]:
    m = re.fullmatch(r"\s*(\d+)\s*(h|j)\s*", o["validite"])
    if not m:
        raise Erreur(f"offre « {o['nom']} » : validité « {o['validite']} » à écrire « 24 h » ou « 7 j »")
    return int(m.group(1)), {"h": "HUR", "j": "DAY"}[m.group(2)]


def tel(code: str) -> str:
    """Règle technique : chaque « # » est encodé en %23 (sinon le navigateur coupe le lien)."""
    return "tel:" + code.replace("#", "%23")


def verifier_codes(d: dict) -> None:
    """Chaque offre a son code direct (#175#221#…), qui commence par le code du menu (#175#)."""
    menu = d["ussd"]
    if not re.fullmatch(r"[#*]\d+#", menu):
        raise Erreur(f"« ussd » : « {menu} » n'est pas un code valide (ex. « #175# »)")
    vus: dict[str, str] = {}
    for o in d["offres"]:
        code = o.get("code", "")
        if not re.fullmatch(re.escape(menu) + r"(\d+#)+", code):
            raise Erreur(f"offre « {o['nom']} » : code « {code} » invalide — attendu {menu} suivi de "
                         f"chiffres et de « # » (ex. « {menu}221# »)")
        if code in vus:
            raise Erreur(f"le code {code} est utilisé par « {vus[code]} » et « {o['nom']} »")
        vus[code] = o["nom"]


def wa_affiche(d: dict) -> str:
    n = re.sub(r"\D", "", d["whatsapp"])
    local = n[3:] if n.startswith("221") else n
    m = re.fullmatch(r"(\d{2})(\d{3})(\d{2})(\d{2})", local)
    return "+221" + NBSP + NBSP.join(m.groups()) if m else "+" + n


def wa_lien(d: dict) -> str:
    from urllib.parse import quote
    msg = "Bonjour, je souhaite des informations sur les nouvelles offres Promobile."
    return f"https://wa.me/{re.sub(r'[^0-9]', '', d['whatsapp'])}?text={quote(msg)}"


def poids_pdf(d: dict) -> str:
    chemin = RACINE / d["catalogue"]["fichier"]
    if not chemin.exists():
        raise Erreur(f"catalogue introuvable : {chemin.name}")
    n = chemin.stat().st_size
    return f"{max(1, round(n / 1024))}{NBSP}Ko" if n < 1048576 else f"{n / 1048576:.1f}".replace(".", ",") + f"{NBSP}Mo"


# ---------------------------------------------------------------- icônes

HORLOGE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>')
FLECHE = ('<svg class="fl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>')


# ---------------------------------------------------------------- fragments HTML

def html_jauge(j: dict, classe: str = "jauge") -> str:
    return (f'<li class="{classe}" style="--r:{j["r"]:.3f}">'
            f'<span class="j-lab">{e(j["label"])}</span>'
            f'<span class="j-val"><s><span class="sr">avant </span>{e(j["avant"])}</s>'
            f'<span class="j-fl" aria-hidden="true">→</span>'
            f'<b><span class="sr">, maintenant </span>{e(j["apres"])}</b></span>'
            f'<span class="j-barre" aria-hidden="true"><span class="j-gain"></span></span></li>')


def html_carte(d: dict, o: dict) -> str:
    js = jauges(o)
    verifier_gain(o, js)
    duree(o)
    plus = f'<span class="gain-plus">{e(o["gainSecondaire"])}</span>' if o.get("gainSecondaire") else ""
    fixes = [x for x in o["details"] if not x.get("change")]
    inclus = ""
    if fixes:
        items = f'<span class="sep" aria-hidden="true"> · </span>'.join(
            f'{e(x["label"])}{NBSP}<b>{e(x["apres"])}</b>' for x in fixes)
        inclus = f'<p class="inclus">Toujours inclus : {items}</p>'
    return (
        f'<article class="carte" id="{e(o["id"])}" data-id="{e(o["id"])}" data-famille="{e(o["famille"])}" '
        f'style="view-transition-name:c-{e(o["id"])}">'
        f'<div class="carte-tete"><h3 class="carte-nom">{e(o["nom"])}</h3>'
        f'<span class="duree">{HORLOGE}{e(o["validiteLongue"])}</span></div>'
        f'<div class="gain-ligne"><p class="gain"><span class="gain-val">{e(o["gain"])}</span>{plus}</p>'
        f'<p class="prix"><span class="sr">Prix : </span>{fcfa(o["prix"])}<small>F</small></p></div>'
        f'<ul class="jauges">{"".join(html_jauge(j) for j in js)}</ul>'
        f'{inclus}'
        f'<a class="activer" href="{tel(o["code"])}" data-code="{e(o["code"])}" aria-label="Activer {e(o["nom"])} '
        f'avec {e(o["code"])}, {e(fcfa(o["prix"]))} francs, {e(o["validiteLongue"])}">'
        f'<span class="act-txt">Activer<span class="act-sous">{e(o["code"])} ou WhatsApp</span></span>{FLECHE}</a>'
        f'</article>')


def html_filtres(d: dict) -> str:
    n = len(d["offres"])
    chips = [f'<button class="chip" type="button" data-f="tous" aria-pressed="true">Toutes'
             f'<span class="nb">{n}</span></button>']
    for cle, fam in d["familles"].items():
        k = sum(1 for o in d["offres"] if o["famille"] == cle)
        if k:
            chips.append(f'<button class="chip" type="button" data-f="{e(cle)}" aria-pressed="false">'
                         f'{e(fam.get("court", cle))}<span class="nb">{k}</span></button>')
    inconnues = {o["famille"] for o in d["offres"]} - set(d["familles"])
    if inconnues:
        raise Erreur(f"famille(s) absente(s) de « familles » : {', '.join(sorted(inconnues))}")
    return ('<div class="filtres" role="group" aria-label="Filtrer les offres">'
            + "".join(chips) + "</div>")


def html_vedette(d: dict) -> str:
    o = offre_vedette(d)
    j = jauges(o)[0]
    return (
        f'<a class="vedette" href="#{e(o["id"])}" aria-label="Exemple : {e(o["nom"])}, '
        f'{e(j["avant"])} avant, {e(j["apres"])} maintenant, toujours {e(fcfa(o["prix"]))} francs">'
        f'<span class="v-tete"><span><b>{e(o["nom"])}</b> · {e(o["validiteLongue"])}</span>'
        f'<span class="v-prix">{fcfa(o["prix"])}{NBSP}F · même prix</span></span>'
        f'<span class="v-gain">{e(o["gain"])}</span>'
        f'<span class="v-jauge" style="--r:{j["r"]:.3f}"><span class="v-avant">{e(j["avant"])}</span>'
        f'<span class="j-barre"><span class="j-gain"></span></span>'
        f'<span class="v-apres">{e(j["apres"])}</span></span></a>')


def html_h1(d: dict) -> str:
    slogan = d["slogan"].strip().rstrip(".")
    if "," in slogan:
        a, b = slogan.split(",", 1)
        return f'<h1 id="slogan">{e(a)}, <em>{e(b.strip())}.</em></h1>'
    return f'<h1 id="slogan">{e(slogan)}.</h1>'


def offre_vedette(d: dict) -> dict:
    o = next((x for x in d["offres"] if x["id"] == d.get("vedette")), None)
    if not o:
        raise Erreur(f"« vedette » : aucune offre n'a l'id « {d.get('vedette')} »")
    return o


def html_code(d: dict) -> str:
    """Le téléphone de « Comment activer » tape le code direct de l'offre vedette."""
    return "".join(f"<span>{e(c)}</span>" for c in offre_vedette(d)["code"])


def html_contact(d: dict) -> str:
    tel_ic = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 '
              '19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.6a2 2 0 0 '
              '1-.5 2.1L8.1 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.6 2.6.7a2 2 0 0 1 1.7 2z"/></svg>')
    wa_ic = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20 3.9A11.8 11.8 0 0 0 1.6 '
             '18.2L0 24l5.9-1.5A11.8 11.8 0 0 0 20 3.9zm-8.1 18.2c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.5.9.9-3.4-.2-.4a9.8 '
             '9.8 0 1 1 8.2 4.5z"/></svg>')
    mail_ic = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/>'
               '<path d="m3 7 9 6 9-6"/></svg>')
    web_ic = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
              '<path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>')
    site = d["siteOfficiel"]
    return (f'<li>{tel_ic}<a href="tel:{e(d["serviceClient"])}">Service client {e(d["serviceClient"])}</a></li>'
            f'<li>{wa_ic}<a href="{e(wa_lien(d))}" target="_blank" rel="noopener">WhatsApp {wa_affiche(d)}</a></li>'
            f'<li>{mail_ic}<a href="mailto:{e(d["email"])}">{e(d["email"])}</a></li>'
            f'<li>{web_ic}<a href="{e(site)}" target="_blank" rel="noopener">'
            f'{e(re.sub(r"^https?://(www[.])?", "", site).rstrip("/"))}</a></li>')


def description(d: dict) -> str:
    return (f"{len(d['offres'])} offres améliorées dès le {d['lancementTexte']} : plus de Go, plus de minutes, "
            f"plus de bonus, au même prix. Activez avec {d['ussd']} ou sur WhatsApp.")


def html_meta(d: dict) -> str:
    a = d["adresse"]
    if not re.fullmatch(r"https://[^\s]+/", a):
        raise Erreur(f"« adresse » doit commencer par https:// et finir par / (reçu : {a})")
    titre = f"{d['slogan']} — Nouvelles offres Promobile"
    lignes = [
        "<!-- généré depuis offres.js par tools/build_page.py — ne pas modifier à la main -->",
        f"<title>{e(titre)}</title>",
        f'<meta name="description" content="{e(description(d))}">',
        f'<link rel="canonical" href="{e(a)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="fr_FR">',
        '<meta property="og:site_name" content="Promobile">',
        f'<meta property="og:title" content="{e(titre)}">',
        f'<meta property="og:description" content="{e(description(d))}">',
        f'<meta property="og:url" content="{e(a)}">',
        f'<meta property="og:image" content="{e(a)}assets/og-image.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="Nouvelles offres Promobile : {e(d["slogan"].lower())}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    return "\n" + "\n".join(lignes) + "\n"


def jsonld(d: dict) -> str:
    a = d["adresse"]
    org = d["siteOfficiel"].rstrip("/") + "/#org"
    offres = []
    for o in d["offres"]:
        n, unite = duree(o)
        offres.append({
            "@type": "Offer",
            "name": o["nom"],
            "url": f"{a}#{o['id']}",
            "description": o["gainDetail"],
            "price": o["prix"],
            "priceCurrency": "XOF",
            "validFrom": d["lancement"],
            "eligibleRegion": "SN",
            "eligibleDuration": {"@type": "QuantitativeValue", "value": n, "unitCode": unite},
            "seller": {"@id": org},
            "itemOffered": {
                "@type": "Service",
                "name": o["nom"],
                "description": " · ".join(f"{x['label']} {x['apres']}" for x in o["details"]),
            },
        })
    graphe = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": org, "name": "Promobile", "url": d["siteOfficiel"],
         "logo": f"{a}assets/logo-promobile.png", "email": d["email"]},
        {"@type": "WebSite", "url": a, "name": "Promobile", "inLanguage": "fr-SN", "publisher": {"@id": org}},
        {"@type": "OfferCatalog", "name": f"Nouvelles offres Promobile — {d['slogan']}", "url": a,
         "itemListElement": offres},
    ]}
    texte = json.dumps(graphe, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'\n<script type="application/ld+json">{texte}</script>\n'


def donnees(d: dict) -> str:
    texte = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"\n<script>var PROMOBILE = {texte};</script>\n"


# ---------------------------------------------------------------- assemblage

def remplacer_zone(page: str, nom: str, contenu: str) -> str:
    motif = re.compile(rf"(<!-- gen:{nom} -->)(.*?)(<!-- /gen:{nom} -->)", re.S)
    page, n = motif.subn(lambda m: m.group(1) + contenu + m.group(3), page)
    if n != 1:
        raise Erreur(f"index.html : la zone gen:{nom} doit apparaître exactement une fois (trouvée {n} fois)")
    return page


def remplacer_textes(page: str, valeurs: dict[str, str]) -> str:
    """<x data-d="cle">…</x> dans le <body>, avant le premier <script> ; éléments feuilles seulement."""
    debut = page.index("<body")
    fin = page.index("<script", debut)
    corps = page[debut:fin]
    vus: set[str] = set()

    def sub(m: re.Match) -> str:
        cle = m.group(3)
        if cle not in valeurs:
            raise Erreur(f"index.html : data-d=\"{cle}\" inconnu (clés possibles : {', '.join(sorted(valeurs))})")
        vus.add(cle)
        return m.group(1) + valeurs[cle] + m.group(5)

    corps = re.sub(r'(<(\w+)\b[^>]*\bdata-d="(\w+)"[^>]*>)([^<]*)(</\2>)', sub, corps)
    return page[:debut] + corps + page[fin:]


def construire(d: dict, page: str) -> str:
    if not d.get("offres"):
        raise Erreur("aucune offre dans offres.js")
    ids = [o["id"] for o in d["offres"]]
    if len(ids) != len(set(ids)):
        raise Erreur("deux offres ont le même « id »")
    verifier_codes(d)
    zones = {
        "meta": html_meta(d),
        "jsonld": jsonld(d),
        "h1": html_h1(d),
        "vedette": html_vedette(d),
        "filtres": html_filtres(d),
        "offres": "".join(html_carte(d, o) for o in d["offres"]),
        "code": html_code(d),
        "contact": html_contact(d),
        "donnees": donnees(d),
    }
    for nom, contenu in zones.items():
        page = remplacer_zone(page, nom, contenu)
    page = remplacer_textes(page, {
        "lancementTexte": e(d["lancementTexte"]),
        "ussd": e(d["ussd"]),
        "nb": str(len(d["offres"])),
        "pdfPoids": poids_pdf(d),
        "waAffiche": wa_affiche(d),
        "serviceClient": e(d["serviceClient"]),
        "vedetteNom": e(offre_vedette(d)["nom"]),
        "vedetteCode": e(offre_vedette(d)["code"]),
    })
    return page


def date_git(*chemins: str) -> str | None:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *chemins], cwd=RACINE,
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def horodatage_git(chemin: str) -> int | None:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", chemin], cwd=RACINE,
                           capture_output=True, text=True, timeout=10)
        return int(r.stdout.strip()) if r.stdout.strip() else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def page_404(d: dict) -> str:
    a = e(d["adresse"])
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable — Promobile</title>
<meta name="robots" content="noindex">
<link rel="icon" type="image/png" href="{a}assets/favicon.png">
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#fff;color:#14181F;
font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;text-align:center;padding:24px}}
img{{height:40px;width:auto}}h1{{font-size:1.6rem;margin:1.2rem 0 .4rem}}p{{margin:0 0 1.4rem;color:#5B616B}}
a.btn{{display:inline-block;background:#E30613;color:#fff;text-decoration:none;font-weight:600;
padding:.85rem 1.4rem;border-radius:999px}}
</style>
</head>
<body>
<main>
<img src="{a}assets/logo-promobile-260.png" alt="Promobile" width="260" height="70">
<h1>Cette page n'existe pas</h1>
<p>Les nouvelles offres Promobile vous attendent sur la page d'accueil.</p>
<a class="btn" href="{a}">Voir les offres</a>
</main>
</body>
</html>
"""


def ecrire(chemin: pathlib.Path, texte: str) -> bool:
    if chemin.exists() and chemin.read_text(encoding="utf-8") == texte:
        return False
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)
    return True


def site(d: dict, dossier: pathlib.Path) -> None:
    if dossier.resolve() == RACINE.resolve() or RACINE.resolve() not in dossier.resolve().parents:
        raise Erreur("--site doit désigner un sous-dossier du projet (ex. _site)")
    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True)
    liste = ["index.html", d["catalogue"]["fichier"]] + [p.name for p in RACINE.glob("google*.html")]
    for nom in liste:
        shutil.copy2(RACINE / nom, dossier / nom)
    shutil.copytree(RACINE / "assets", dossier / "assets")
    a = d["adresse"]
    lastmod = date_git("offres.js", "index.html") or dt.date.today().isoformat()
    ecrire(dossier / "sitemap.xml",
           '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"  <url><loc>{e(a)}</loc><lastmod>{lastmod}</lastmod></url>\n</urlset>\n")
    ecrire(dossier / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {a}sitemap.xml\n")
    ecrire(dossier / "404.html", page_404(d))
    pdf, src = horodatage_git(d["catalogue"]["fichier"]), horodatage_git("offres.js")
    if pdf and src and pdf < src:
        avertir("Le PDF est plus ancien que offres.js : pensez à le régénérer "
                "(python3 tools/build_catalogue.py) ou à déposer la nouvelle version du Marketing.")
    print(f"OK {dossier.relative_to(RACINE)}/ — {sum(1 for _ in dossier.rglob('*') if _.is_file())} fichiers")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true", help="vérifie seulement que index.html est à jour")
    p.add_argument("--site", metavar="DOSSIER", help="crée aussi le dossier publiable")
    args = p.parse_args()
    try:
        d = charger()
        actuel = PAGE.read_text(encoding="utf-8")
        nouveau = construire(d, actuel)
        if args.check:
            if nouveau != actuel:
                print("index.html n'est pas à jour : lancez python3 tools/build_page.py", file=sys.stderr)
                return 1
            print("OK index.html est à jour")
            return 0
        print("OK index.html mis à jour" if ecrire(PAGE, nouveau) else "OK index.html déjà à jour")
        if args.site:
            site(d, (RACINE / args.site))
        return 0
    except Erreur as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as err:
        print(f"ERREUR : offres.js n'est pas du JSON valide après « = » ({err})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
