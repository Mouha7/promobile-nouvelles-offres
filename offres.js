/* ============================================================
   PROMOBILE — Nouvelles offres : SOURCE UNIQUE DE VÉRITÉ
   ------------------------------------------------------------
   Ce fichier alimente :
     • la page (index.html) : cartes, textes, données inline,
       JSON-LD, adresses — via tools/build_page.py
     • les messages WhatsApp préremplis
     • le catalogue PDF (tools/build_catalogue.py)

   Règles d'édition (lire docs/GUIDE.md) :
     • Tout ce qui suit « = » est du JSON strict :
       guillemets doubles, pas de virgule finale, pas de commentaire.
     • Sur github.com : modifier ici puis « Commit » suffit, le site
       est reconstruit et publié automatiquement (onglet Actions).
     • En local : python3 tools/build_page.py après chaque modification.
     • Le PDF n'est PAS mis à jour automatiquement : le régénérer
       (python3 tools/build_catalogue.py) ou le remplacer.
   ============================================================ */
var PROMOBILE = {
  "slogan": "Plus de valeur, au même prix",
  "lancement": "2026-10-21",
  "lancementTexte": "21 octobre 2026",
  "adresse": "https://mouha7.github.io/promobile-nouvelles-offres/",
  "vedette": "pronet-3go",

  "ussd": "#175#",
  "whatsapp": "221755250000",
  "serviceClient": "1675",
  "email": "contact@promobile.sn",
  "siteOfficiel": "https://www.promobile.sn",

  "mesure": { "umami": "cb54054d-f849-4d20-b867-b991ca0dbe94" },

  "sloganWolof": "Dose Bi Yokkuti Na !!!",
  "sloganWolofAccent": "Yokkuti Na",
  "sloganWolofSens": "le niveau a augmenté",

  "reseau": {
    "badge": "4G+",
    "court": "Meilleur réseau du Sénégal",
    "chiffre": "98 % de couverture",
    "complet": "Meilleur réseau 4G+ du Sénégal, avec 98 % de couverture"
  },

  "recharge": {
    "titre": "Pas assez de crédit ? Rechargez",
    "texte": "Achetez du crédit avec nos partenaires Wave ou Max it (Orange Money), sur l'app Promobile ou en ligne.",
    "canaux": [
      { "id": "wave", "nom": "Wave", "detail": "Achat crédit", "icone": "assets/paiement/wave.png", "android": "com.wave.personal", "ios": "1523884528" },
      { "id": "maxit", "nom": "Max it", "detail": "Orange Money", "icone": "assets/paiement/orange-money.png", "android": "com.orange.myorange.osn", "ios": "1039327980" },
      { "id": "promobile", "nom": "Promobile", "detail": "L'application", "icone": "assets/app-promobile.png", "android": "com.promobile.app", "ios": "6449710285" },
      { "id": "en-ligne", "nom": "En ligne", "detail": "promobile.sn", "url": "https://www.promobile.sn/erecharge" }
    ]
  },

  "catalogue": {
    "fichier": "Catalogue_Offres_Promobile.pdf",
    "poidsAffiche": "moins de 1 Mo"
  },

  "familles": {
    "ProNET":  { "prefixe": "PRO'", "suffixe": "NET",  "libelle": "Offres Internet", "court": "Internet" },
    "ProMIX":  { "prefixe": "PRO'", "suffixe": "MIX",  "libelle": "Offres Mix", "court": "Appels + Internet" },
    "ProMINI": { "prefixe": "PRO'", "suffixe": "MINI", "libelle": "Bonus & Internet", "court": "Bonus + Internet" }
  },

  "offres": [
    {
      "id": "promini-175",
      "code": "#175#12#",
      "famille": "ProMINI",
      "nom": "ProMINI 175",
      "ancienNom": "ProMINI 175",
      "prix": 175,
      "validite": "24 h",
      "validiteLongue": "24 heures",
      "gain": "Bonus ×2",
      "gainDetail": "2\u00a0000 F de bonus au lieu de 1\u00a0000 F",
      "details": [
        { "label": "Bonus appels", "avant": "1\u00a0000 F", "apres": "2\u00a0000 F tous réseaux", "change": true },
        { "label": "Internet", "avant": "175 Mo", "apres": "175 Mo", "change": false }
      ]
    },
    {
      "id": "pronet-3go",
      "code": "#175#221#",
      "famille": "ProNET",
      "nom": "ProNET 3 Go",
      "ancienNom": "ProNET 2,5 Go",
      "prix": 975,
      "validite": "7 j",
      "validiteLongue": "7 jours",
      "gain": "+0,5 Go",
      "gainDetail": "3 Go au lieu de 2,5 Go",
      "details": [
        { "label": "Internet", "avant": "2,5 Go", "apres": "3 Go", "change": true }
      ]
    },
    {
      "id": "pronet-4go",
      "code": "#175#231#",
      "famille": "ProNET",
      "nom": "ProNET 4 Go",
      "ancienNom": "ProNET 3,5 Go",
      "prix": 1375,
      "validite": "30 j",
      "validiteLongue": "30 jours",
      "gain": "+0,5 Go",
      "gainDetail": "4 Go au lieu de 3,5 Go",
      "details": [
        { "label": "Internet", "avant": "3,5 Go", "apres": "4 Go", "change": true }
      ]
    },
    {
      "id": "pronet-m-6-5go",
      "code": "#175#232#",
      "famille": "ProNET",
      "nom": "ProNET (M) 6,5 Go",
      "ancienNom": "ProNET (M) 5,5 Go",
      "prix": 1975,
      "validite": "30 j",
      "validiteLongue": "30 jours",
      "gain": "+1 Go",
      "gainDetail": "6,5 Go au lieu de 5,5 Go",
      "details": [
        { "label": "Internet", "avant": "5,5 Go", "apres": "6,5 Go", "change": true }
      ]
    },
    {
      "id": "promix-475",
      "code": "#175#31#",
      "famille": "ProMIX",
      "nom": "ProMIX 475",
      "ancienNom": "ProMIX 475",
      "prix": 475,
      "validite": "48 h",
      "validiteLongue": "48 heures",
      "gain": "+20 min",
      "gainDetail": "100 min au lieu de 80 min",
      "details": [
        { "label": "Appels", "avant": "80 min", "apres": "100 min", "change": true },
        { "label": "SMS", "avant": "50", "apres": "50", "change": false },
        { "label": "Internet", "avant": "500 Mo", "apres": "500 Mo", "change": false }
      ]
    },
    {
      "id": "promix-975",
      "code": "#175#32#",
      "famille": "ProMIX",
      "nom": "ProMIX 975",
      "ancienNom": "ProMIX 975",
      "prix": 975,
      "validite": "7 j",
      "validiteLongue": "7 jours",
      "gain": "+0,5 Go",
      "gainSecondaire": "+50 SMS",
      "gainDetail": "2 Go et 100 SMS au lieu de 1,5 Go et 50 SMS",
      "details": [
        { "label": "Appels", "avant": "120 min", "apres": "120 min", "change": false },
        { "label": "SMS", "avant": "50", "apres": "100", "change": true },
        { "label": "Internet", "avant": "1,5 Go", "apres": "2 Go", "change": true }
      ]
    },
    {
      "id": "promix-1375",
      "code": "#175#331#",
      "famille": "ProMIX",
      "nom": "ProMIX 1375",
      "ancienNom": "ProMIX 1375",
      "prix": 1375,
      "validite": "30 j",
      "validiteLongue": "30 jours",
      "gain": "+0,5 Go",
      "gainDetail": "3 Go au lieu de 2,5 Go",
      "details": [
        { "label": "Appels", "avant": "150 min", "apres": "150 min", "change": false },
        { "label": "SMS", "avant": "100", "apres": "100", "change": false },
        { "label": "Internet", "avant": "2,5 Go", "apres": "3 Go", "change": true }
      ]
    },
    {
      "id": "promix-1975",
      "code": "#175#332#",
      "famille": "ProMIX",
      "nom": "ProMIX 1975",
      "ancienNom": "ProMIX 1975",
      "prix": 1975,
      "validite": "30 j",
      "validiteLongue": "30 jours",
      "gain": "+120 min",
      "gainDetail": "300 min au lieu de 180 min",
      "details": [
        { "label": "Appels", "avant": "180 min", "apres": "300 min", "change": true },
        { "label": "SMS", "avant": "100", "apres": "100", "change": false },
        { "label": "Internet", "avant": "3,5 Go", "apres": "3,5 Go", "change": false }
      ]
    }
  ]
};
