# Nouvelles offres Promobile — mini-site

« Plus de valeur, au même prix » : page unique présentant les 8 offres améliorées
(ProMINI, ProNET, ProMIX) lancées le 21 octobre 2026, avec activation en un geste
(code USSD direct par offre, ex. `#175#221#`, ou WhatsApp) et téléchargement du catalogue PDF.
En haut de page, l'offre vedette crève la page blanche, passe devant et bat ; confettis sur toute la page.

- **Avant → Après** : chaque carte montre l'ancien volume et ce qui s'ajoute, au même prix.
- **Statique et léger** : environ 76 Ko au premier chargement, polices, animations et confettis compris ; lisible à 320 px.
- **Une seule source de vérité** : `offres.js` alimente les cartes, les messages WhatsApp, le
  référencement (JSON-LD, sitemap) et le PDF. `tools/build_page.py` (Python standard, sans
  dépendance) réécrit les zones générées de `index.html`.
- **Publication automatique** : GitHub Pages via GitHub Actions, à chaque modification de `main`.
- **Charte Promobile** : blanc, rouge `#E30613`, noir `#14181F`, accent jaune `#FFCF00` ;
  Poppins et Barlow Condensed auto-hébergées (licence OFL).
- **Accessible** : contenu lisible sans JavaScript ni animation, mouvement réduit respecté.
- **Mesure sans données personnelles** : événements prêts pour Umami / Plausible / GA4.

Voir [docs/GUIDE.md](docs/GUIDE.md) pour modifier les offres, remplacer le PDF, brancher le
domaine et la mesure.

## Développement

```bash
python3 tools/build_page.py          # régénère index.html depuis offres.js
python3 tools/build_page.py --check  # vérifie que index.html est à jour (code 1 sinon)
python3 -m http.server 8080          # puis http://localhost:8080
pip install -r tools/requirements.txt
python3 tools/build_catalogue.py     # régénère Catalogue_Offres_Promobile.pdf
python3 tools/build_og_image.py      # régénère assets/og-image.png
```
