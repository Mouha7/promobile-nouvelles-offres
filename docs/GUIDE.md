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
| `details`        | une barre par ligne ; `change: true` = avant → après en rouge, sinon barre pleine « inclus » | voir le fichier |

Les lignes `change: true` doivent avoir des valeurs lisibles (`"2,5 Go"`, `"1 000 F"`, `"80 min"`,
`"50"`), la même unité avant et après, et une valeur après plus grande : c'est ce qui dessine la
jauge. Un avertissement s'affiche si le `gain` saisi ne correspond pas aux lignes avant/après.

Astuce : ` ` dans un texte = espace insécable (évite « 1 000 F » coupé en fin de ligne).

Paramètres globaux : `lancementTexte` (date affichée), `ussd` (**`#175#`**, le menu général ; chaque
offre a en plus son `code` direct, qui doit commencer par `#175#` et finir par `#`), `whatsapp` (numéro
international sans « + », ex. `221755250000`), `serviceClient`, `email`, `adresse` (adresse du site,
voir § 6), `vedette` (l'offre rejouée dans le haut de page, par son `id`), `mesure` (identifiant du site
Umami, voir § 8 ; vide = aucune mesure).

Textes de campagne (facultatifs : un champ absent fait disparaître l'élément) :

- `sloganWolof` : le slogan du moment sous le titre, sur un coup de surligneur jaune (ex. `"Dose Bi Yokkuti Na !!!"`).
  La ponctuation finale s'affiche en rouge, ainsi que la partie donnée dans `sloganWolofAccent` (ex. `"Yokkuti Na"`). `sloganWolofSens` donne sa traduction, lue par les lecteurs d'écran et
  affichée au survol.
- `reseau` : la ligne en pied de la carte phare. `badge` (`"4G+"`), `court` (la phrase affichée), `chiffre`
  (facultatif, en jaune après un point ; le tout tient sur une ligne : rester court) et `complet` (la phrase entière, lue par les lecteurs d'écran). Garder la source du chiffre de
  couverture annoncé.
- `recharge` : la 4e étape de « Comment activer ». `titre`, `texte` et `canaux`. Chaque canal a un `id` (`wave`,
  `maxit`, `promobile`, `en-ligne`), un `nom`, un `detail` (sous-titre), une `icone` facultative (image carrée,
  ex. `assets/paiement/wave.png` ; les logos Wave et Orange Money, fournis par Promobile, sont rangés dans
  `assets/paiement/`, l'icône de l'app dans `assets/app-promobile.png`), puis soit
  `url` (un site, en `https://`), soit `android` (identifiant Google Play, ex. `com.wave.personal`) **et** `ios`
  (numéro App Store, ex. `1523884528`). Une appli ouvre sa fiche Play Store ; sur iPhone, sa fiche App Store. La fiche
  affiche « Ouvrir » si l'appli est déjà installée. Pour ouvrir **directement** l'app Promobile (et une offre précise),
  il faut un lien profond fourni par son éditeur (TelEtCom) : le mettre alors dans `url`.

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

Ajouter la source au lien selon le canal. Umami la range dans son rapport **UTM**, et la page la joint à chaque
événement (propriété `source`) :

- SMS : `https://ADRESSE/?utm_source=sms`
- WhatsApp : `https://ADRESSE/?utm_source=whatsapp`
- Réseaux sociaux : `https://ADRESSE/?utm_source=facebook` (ou `instagram`, `tiktok`…)
- Une campagne précise : ajouter `&utm_campaign=lancement-oct26`

La forme courte `?src=sms` marche aussi pour les événements, mais Umami ne la range pas dans son rapport UTM.
La source est retenue pendant toute la visite, même après un rechargement.

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

**Intro du haut de page (environ 4 s, à chaque chargement)** : la zone de la carte est d'abord vide et blanche ;
une ombre pousse derrière la page, puis **la page se fissure selon la frontière exacte du Sénégal** (clin d'œil) : la
pièce de papier en forme de pays est éjectée et laisse un trou rouge en forme de Sénégal, où la Gambie reste en
papier blanc. La page se déchire ensuite tout autour, et la carte (l'offre `vedette`) la crève et passe devant.
**Téléphone et ordinateur jouent exactement la même scène** : elle est réduite proportionnellement sur téléphone
(même carte avec le « +0,5 Go », mêmes lambeaux, même rythme) ; seule la place du texte change.
Sur tablette (720 à 1039 px de large), le texte et la carte sont côte à côte comme sur ordinateur ; le titre et le
slogan suivent alors la largeur de leur colonne, pour ne jamais passer sous la déchirure. Des confettis (bibliothèque canvas-confetti 1.9.4, licence ISC, intégrée à la page) jaillissent de derrière la
carte ; en même temps, une pluie tombe sur toute la largeur et deux canons tirent depuis les coins bas de l'écran,
si bien que tout l'écran est couvert pendant environ 3 s. Les lambeaux de papier restent en collerette autour de
la carte, et des confettis restent posés autour d'elle et dans les marges, où ils flottent doucement.
Au même moment, sous le titre, le coup de surligneur jaune se dessine derrière le slogan wolof, qui « tamponne »
puis fait un petit signe toutes les 5 s tant que le haut de page est à l'écran.
Si la page s'ouvre ailleurs qu'en haut (lien vers `#offres` ou vers une offre), la zone de la carte reste blanche
et l'intro se joue quand on remonte jusqu'à elle. Un rechargement repart toujours du haut de la page.

**Page vivante** (choix du client) : après l'apparition du nouveau volume, la carte bat en continu ; les confettis
posés flottent et le téléphone de « Comment activer » (complet, sur mobile aussi) tape les codes en boucle,
touche par touche. Chaque zone ne s'anime que lorsqu'elle
est à l'écran et se met en pause dès qu'on la quitte (batterie), jusqu'au retour. Note : sans bouton pause, ces
mouvements continus ne respectent pas la règle d'accessibilité WCAG 2.2.2 ; c'est un choix assumé.

**Accessibilité et performances** : si le téléphone demande « Réduire les animations » (iPhone : Réglages >
Accessibilité > Mouvement ; Android : « Supprimer les animations »), le site joue une **version douce** : la fissure
« Sénégal » se trace, la carte et sa collerette arrivent en fondu, le surligneur se dessine, la jauge se remplit et le
téléphone tape le code ; sans 3D, secousses, rebonds, explosion de confettis ni battement. Pour vérifier sur un
téléphone ce qu'il déclare, ouvrir l'adresse du site suivie de `?diag`. Le titre n'est jamais animé
(il reste l'élément affiché le plus vite). Sur les téléphones à faible mémoire, les confettis sont moins nombreux.

Réglages (dans `index.html`, CSS de `.hero`) : les temps de l'intro (`--tsn` fissure « Sénégal », `--tv0` éjection
de la pièce, `--tc` ouverture des lambeaux, `--tz` passage devant, etc.) et, dans le script de mouvement (fonction
`feu`), le nombre de confettis (`N`), leur vitesse (`startVelocity`) et leur durée de vie (`ticks`). La vitesse des
confettis posés se règle par `--fd` (durée d'un aller). Les tailles de la carte du haut sont en `cqw` (pourcentage de
la largeur de la scène) : elles suivent la scène sur tous les écrans.

La frontière vient de **Natural Earth 1:10m** (domaine public), conservée dans `tools/data/senegal.geojson`.
`tools/build_dechirure.py` la projette, la simplifie (constante `TOLERANCE`) et la place sans déformation dans la
boîte du papier (rapport `BOITE` = 1,82, le même que `.papier{aspect-ratio}` dans le CSS). `build_page.py` l'appelle
et écrit la zone `gen:papier`. Les lambeaux et les fissures qui partent du centre sont calculés dans `<head>`
(fonction `dechirure`, graine fixe : identiques à chaque visite).

## 8. Mesure d'audience (Umami Cloud) — sans cookie ni donnée personnelle

La page est mesurée par **Umami Cloud**. Umami ne pose pas de cookie et ne garde aucune donnée personnelle, donc
pas de bandeau de consentement. Les mentions légales le disent déjà : « seules des statistiques anonymes de
consultation sont mesurées ».

**Réglage** : l'identifiant du site Umami est dans `offres.js`, champ `"mesure": { "umami": "…" }`. `build_page.py`
écrit la balise dans `<head>` (zone `gen:mesure`).
- **Vide** : aucune mesure, la page ne charge rien.
- **Mal formé** : la construction s'arrête avec un message clair.
- **Seul le site en ligne est compté** : la balise ne retient que l'hôte de `adresse`. Les tests en local et les
  aperçus ne faussent donc pas les chiffres, et au passage au nom de domaine (§ 6), changer `adresse` suffit.
- **Les visiteurs qui ont activé « Ne pas me pister »** ne sont pas comptés.

**Où lire les chiffres** : cloud.umami.is, puis le site. On y trouve :
- **Vue d'ensemble** : visiteurs, visites, pages vues, durée de visite ;
- **Sources** et rapport **UTM** : d'où viennent les visiteurs (liens du § 5) ;
- **Appareils**, navigateurs, systèmes, pays et villes ;
- **Events** : les événements ci-dessous, filtrables par propriété ;
- **Realtime** : les visites en direct, utile pour vérifier que la mesure marche.

Les chiffres sont un **minimum** : les bloqueurs de publicité et « Ne pas me pister » en écartent une partie.

**Événements envoyés par la page** (en plus des pages vues, qu'Umami compte seul) :

| Événement | Quand | Propriétés |
|---|---|---|
| `vu_offres` | la liste des offres apparaît à l'écran (une fois par visite) | — |
| `vu_comment` | « Activer une offre prend dix secondes » apparaît | — |
| `vu_catalogue` | le bloc du PDF apparaît | — |
| `vu_pied` | le pied de page apparaît (page lue jusqu'au bout) | — |
| `offre_clic` | une carte d'offre est touchée (la feuille d'activation s'ouvre) | `offre` |
| `vedette_clic` | la carte du haut (ProNET 3 Go) est touchée | `offre` |
| `activer_ussd` | « Activer » : le clavier s'ouvre avec le code | `offre` |
| `activer_whatsapp` | activation par WhatsApp | `offre` |
| `copier_code` | « Copier le code » (iPhone surtout) | `offre` |
| `filtre` | un filtre est choisi | `famille` |
| `recharge` | un moyen de recharge est touché | `canal` (Wave, Max it, Promobile, En ligne) |
| `telecharger_pdf` | le catalogue PDF est téléchargé | `position` (`haut` ou `bas`) |

Chaque événement porte aussi `source` quand la visite vient d'un lien du § 5. `offre` vaut l'identifiant de la
carte (`pronet-3go`, `promix-975`…). Un événement émis avant le chargement d'Umami est gardé puis envoyé : rien ne
se perd au chargement.

**Entonnoir à créer** (Umami › Reports › Funnel) : `vu_offres` → `offre_clic` → `activer_ussd`. Il montre combien
de visiteurs voient les offres, en ouvrent une, puis lancent l'activation. Un second entonnoir, avec
`activer_whatsapp` en dernière étape, mesure WhatsApp. **Objectifs** (Reports › Goals) : `activer_ussd` et
`activer_whatsapp`, les deux gestes qui comptent.

**Partager les chiffres** sans donner l'accès au compte : Settings › Websites › le site › Edit › **Share URL**
(lien en lecture seule, à donner à Promobile).

**Quota** : l'offre gratuite (Hobby) compte environ 100 000 événements par mois et garde 6 mois d'historique. Une
page vue compte pour un événement, chaque événement aussi, et **chaque propriété en compte un de plus**. Une visite
moyenne coûte une dizaine d'événements, soit **environ 10 000 visites par mois**. Au-delà : passer à l'offre
payante, ou retirer des propriétés dans `track()` (script principal de `index.html`).

**Recette** : ouvrir le site avec `?utm_source=test`, toucher une offre, puis vérifier dans Umami › Realtime.
Les événements sont aussi visibles dans la console du navigateur (préfixe `[mesure]`, niveau « Verbose »).

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
- [ ] Les visites et les événements remontent dans Umami (Realtime), avec l'offre et la source.
