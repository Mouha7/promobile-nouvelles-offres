# Guide d'exploitation — mini-site « Nouvelles offres Promobile »

Site statique d'une page, publié par **GitHub Pages**. Aucun serveur, aucune base de données.

```
offres.js                       LA source de vérité : offres, prix, validités, code, WhatsApp, date, adresse
index.html                      la page (design + zones générées depuis offres.js)
Catalogue_Offres_Promobile.pdf  le catalogue téléchargé par les clients
assets/                         logo, favicon, image de partage (og-image.png), polices
tools/build_page.py             régénère la page depuis offres.js (fait automatiquement à chaque publication)
.github/workflows/pages.yml     l'automate de publication (GitHub Actions)
```

## 1. Comment le site est publié

À chaque modification enregistrée sur la branche `main` (depuis github.com ou un `git push`),
l'automate **régénère la page depuis `offres.js` puis la publie**, en 1 minute environ.

- Onglet **Actions** du dépôt : **coche verte** = la nouvelle version est en ligne ;
  **croix rouge** = **rien n'a été publié**, l'ancienne version reste en ligne. Cliquer sur la
  ligne en rouge pour lire le message (souvent une virgule ou un guillemet dans `offres.js`).
- Le fichier `index.html` du dépôt peut garder d'anciennes cartes après une modification faite sur
  github.com : c'est normal et sans effet, le site en ligne est toujours reconstruit.
- Avant de travailler en local : `git pull`, puis `python3 tools/build_page.py`.

## 2. Modifier une offre, un prix, une validité, la date, le numéro WhatsApp

Tout est dans `offres.js`, et nulle part ailleurs. Sur github.com : ouvrir `offres.js`, icône
crayon, modifier, « Commit changes ». Les cartes, les jauges avant → après, les messages
WhatsApp, le référencement (JSON-LD) et le sitemap suivent.

Règles : ce qui suit `var PROMOBILE =` est du JSON strict — guillemets doubles,
pas de virgule après le dernier élément, pas de commentaire. En local, vérifier avec
`python3 tools/build_page.py` : il s'arrête avec un message clair si une valeur est illisible.

Champs d'une offre :

| Champ            | Rôle                                                   | Exemple                    |
|------------------|--------------------------------------------------------|----------------------------|
| `nom`            | nom affiché et repris dans le message WhatsApp         | `"ProNET 3 Go"`            |
| `code`           | code USSD direct : la carte le compose, l'offre s'active sans menu | `"#175#221#"` |
| `prix`           | en F CFA, nombre sans espace                           | `975`                      |
| `validite`       | forme courte, **obligatoirement** `N h` ou `N j`       | `"7 j"`                    |
| `validiteLongue` | affichée sur la carte et dans WhatsApp                 | `"7 jours"`                |
| `gain`           | l'élément le plus visible de la carte                  | `"+0,5 Go"`                |
| `gainSecondaire` | facultatif, pastille jaune à côté du gain              | `"+50 SMS"`                |
| `gainDetail`     | phrase pour le référencement                           | `"3 Go au lieu de 2,5 Go"` |
| `details`        | lignes avant → après ; `change: true` = jauge rouge    | voir le fichier            |

Les lignes `change: true` doivent avoir des valeurs lisibles (`"2,5 Go"`, `"1 000 F"`, `"80 min"`,
`"50"`), la même unité avant et après, et une valeur après plus grande : c'est ce qui dessine la
jauge. Un avertissement s'affiche si le `gain` saisi ne correspond pas aux lignes avant/après.

Astuce : ` ` dans un texte = espace insécable (évite « 1 000 F » coupé en fin de ligne).

Paramètres globaux : `lancementTexte` (date affichée), `ussd` (**`#175#`**, le menu général ; chaque
offre a en plus son `code` direct, qui doit commencer par `#175#` et finir par `#`), `whatsapp` (numéro
international sans « + », ex. `221755250000`), `serviceClient`, `email`, `adresse` (adresse du site,
voir § 6), `vedette` (l'offre rejouée dans le haut de page, par son `id`).

**Changer un prix ne met pas à jour le PDF** : le régénérer (§ 3) ou déposer la nouvelle version du
Marketing. L'automate affiche un avertissement si le PDF est plus ancien que `offres.js`.

## 3. Remplacer le catalogue PDF (équipe Marketing)

1. Nommer le nouveau fichier exactement `Catalogue_Offres_Promobile.pdf` (moins de 2 Mo).
2. Sur github.com : **Add file › Upload files**, déposer le fichier, « Commit changes ».
3. C'est tout : le lien ne change pas, le poids affiché à côté des boutons se met à jour tout seul.

Pour régénérer le PDF « maison » à partir de `offres.js` :
`pip install -r tools/requirements.txt` puis `python3 tools/build_catalogue.py`.

## 4. Points à confirmer avant la diffusion (cahier des charges § 6)

- [ ] Date de lancement : **21 octobre 2026** retenue (`lancementTexte`).
- [ ] Validité ProMIX 475 : **24 h** retenue — si 48 h, changer `validite` et `validiteLongue`.
- [ ] Numéro WhatsApp officiel : **75 525 00 00** repris du site promobile.sn (`whatsapp`).
- [x] Codes d'activation : **un code direct par offre**, testés par le client le 19/10/2026
      (ex. ProNET 3 Go = `#175#221#`, lien `tel:%23175%23221%23`). `#175#` seul ouvre le menu.
- [ ] PDF final fourni par Marketing (sinon le PDF généré reste en place).
- [ ] **iPhone** : Apple bloque les liens d'appel contenant `#` ou `*`. Sur iPhone, la page met donc
      « Copier le code » en premier (le client colle le code dans l'app Téléphone). À valider avec le client.

## 5. Liens à diffuser (mesure par source)

Ajouter `?src=` au lien selon le canal ; la source est jointe à chaque événement mesuré :

- SMS : `https://ADRESSE/?src=sms`
- WhatsApp : `https://ADRESSE/?src=whatsapp`
- Réseaux sociaux : `https://ADRESSE/?src=social` (ou `facebook`, `instagram`, `tiktok`…)

## 6. Nom de domaine (ex. `offres.promobile.sn`)

Le site est publié par l'automate (GitHub Actions) : un fichier `CNAME` dans le dépôt est **ignoré**,
le domaine se règle dans GitHub.

1. **D'abord**, vérifier le domaine sur GitHub (protège contre la prise de contrôle du sous-domaine) :
   profil › Settings › Pages › « Add a domain », puis ajouter l'enregistrement TXT indiqué
   (`_github-pages-challenge-…`) dans la zone DNS de `promobile.sn`.
2. Dans la zone DNS : `offres` **CNAME** `mouha7.github.io.` (pas de joker `*`). Si la zone a des
   enregistrements CAA, l'un d'eux doit autoriser `letsencrypt.org`.
3. Dépôt › Settings › Pages › Custom domain : `offres.promobile.sn` › Save
   (ou `gh api -X PUT repos/Mouha7/promobile-nouvelles-offres/pages -f cname=offres.promobile.sn`).
4. Quand le certificat est prêt (jusqu'à 24 h) : cocher **Enforce HTTPS**.
5. Dans `offres.js` : `"adresse": "https://offres.promobile.sn/"` › Commit. Les liens canoniques,
   l'image de partage WhatsApp, le JSON-LD, le sitemap et `robots.txt` suivent. L'ancienne adresse
   github.io redirige automatiquement.

`robots.txt` et `sitemap.xml` ne sont lus par Google qu'à la racine d'un domaine : ils deviennent
utiles à cette étape. **Search Console** : propriété « Préfixe d'URL » `https://offres.promobile.sn/`,
vérifiée par fichier HTML (un TXT est impossible sur un sous-domaine en CNAME) — déposer le fichier
`google….html` à la racine du dépôt, l'automate le publie ; puis soumettre `sitemap.xml`.

**Aperçu WhatsApp** : WhatsApp garde l'image en cache. Pour la changer, renommer le fichier
(`og-image-v2.png`, et mettre à jour `tools/build_page.py`) et partager le lien avec `?v=2`.

## 7. Animations

**Intro du haut de page (environ 3 s, à chaque chargement)** : la zone de la carte est d'abord vide et blanche ;
une ombre pousse derrière la page, la page se fissure, se déchire, et la carte (l'offre `vedette`) la crève et passe
devant. Des confettis (bibliothèque canvas-confetti 1.9.4, licence ISC, intégrée à la page) jaillissent de derrière la
carte ; en même temps, une pluie tombe sur toute la largeur et deux canons tirent depuis les coins bas de l'écran,
si bien que tout l'écran est couvert pendant environ 3 s. Les lambeaux de papier restent en collerette autour de
la carte, et des confettis restent posés autour d'elle et dans les marges, où ils flottent doucement.
Si la page s'ouvre ailleurs qu'en haut (lien vers `#offres` ou vers une offre), la zone de la carte reste blanche
et l'intro se joue quand on remonte jusqu'à elle. Un rechargement repart toujours du haut de la page.

**Page vivante** (choix du client) : après l'apparition du nouveau volume, la carte bat en continu ; les confettis
posés flottent et le téléphone de « Comment activer » tape les codes en boucle. Chaque zone ne s'anime que lorsqu'elle
est à l'écran et se met en pause dès qu'on la quitte (batterie), jusqu'au retour. Note : sans bouton pause, ces
mouvements continus ne respectent pas la règle d'accessibilité WCAG 2.2.2 ; c'est un choix assumé.

**Accessibilité et performances** : les personnes qui ont activé « Supprimer les animations » dans leur téléphone
voient directement la composition finale, immobile (carte posée dans sa collerette). Le titre n'est jamais animé
(il reste l'élément affiché le plus vite). Sur les téléphones à faible mémoire, les confettis sont moins nombreux.

Réglages (dans `index.html`, CSS de `.hero`) : les temps de l'intro (`--tc` fissure, `--tz` passage devant, etc.)
et, dans le script de mouvement (fonction `feu`), le nombre de confettis (`N`), leur vitesse (`startVelocity`) et
leur durée de vie (`ticks`). La vitesse des confettis posés se règle par `--fd` (durée d'un aller). La forme de la déchirure est calculée dans `<head>`
(fonction `dechirure`, graine fixe : elle est identique à chaque visite).

## 8. Mesure (F5) — sans données personnelles

La page émet ces événements : `visite`, `offre_clic`, `activer_ussd`, `activer_whatsapp`,
`copier_code`, `telecharger_pdf` (+ `filtre`), chacun avec `offre` et `source`.
Ils sont transmis à l'outil présent dans la page. Recommandé : **Umami Cloud**
(gratuit jusqu'à 100 000 événements/mois, sans cookie, conforme RGPD) :

1. Créer un compte sur umami.is, ajouter le site, copier l'identifiant (`data-website-id`).
2. Dans `index.html`, bloc « MESURE (F5) » en haut : décommenter la ligne Umami et coller l'identifiant.
3. Les événements apparaissent dans Umami → Events, filtrables par `offre` et `source`.

Plausible (payant) ou Google Analytics 4 fonctionnent aussi sans rien changer d'autre.
Sans outil, les événements restent visibles dans la console du navigateur (préfixe `[mesure]`,
niveau « Verbose » à activer), utile pour la recette.

## 9. Recette (critères de validation § 7)

- [ ] Les 8 cartes affichent les prix, volumes et validités du catalogue officiel.
- [ ] Android : chaque carte ouvre le clavier avec **son** code déjà saisi (ex. `#175#221#`) et
      l'offre s'active directement.
- [ ] iPhone : « Copier le code » copie le code de l'offre, à coller dans l'app Téléphone.
- [ ] Chaque carte ouvre WhatsApp avec le bon message prérempli.
- [ ] Tester aussi **depuis un lien ouvert dans WhatsApp, Facebook et Instagram** (navigateurs
      intégrés, d'où vient l'essentiel du trafic) : clavier, WhatsApp et PDF.
- [ ] Le PDF se télécharge et s'ouvre sur un téléphone d'entrée de gamme.
- [ ] L'aperçu du lien collé dans WhatsApp montre l'image et le titre.
- [ ] Les événements remontent dans l'outil de mesure, avec l'offre et la source.
