# GNU Astro Galery

**GNU Astro Galery** est un générateur de galerie Web statique (HTML5 / CSS3 / Bootstrap 5) dédié aux images produites par le **télescope intelligent Seestar S50**.

Le projet vise une approche à la fois **esthétique**, **scientifique** et **documentaire**, en mettant l’accent sur :
- la **page objet** comme unité centrale,
- l’enrichissement automatique des données astronomiques,
- la **traçabilité** (métadonnées, catalogues, astrométrie),
- et une **navigation claire** adaptée à la diffusion publique.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Philosophie de navigation](#philosophie-de-navigation)
- [Structure des données Seestar](#structure-des-données-seestar)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Catalogue Messier (XLSX)](#catalogue-messier-xlsx)
- [Enrichissement via SIMBAD](#enrichissement-via-simbad)
- [Pages objet](#pages-objet)
- [Astrométrie](#astrométrie)
- [Cache astrométrie](#cache-astrométrie)
- [Règles d’inclusion / exclusion](#règles-dinclusion--exclusion)
- [SEO et données structurées](#seo-et-données-structurées)
- [Dépannage](#dépannage)
- [Sécurité et confidentialité](#sécurité-et-confidentialité)
- [Publication](#publication)
- [Licence](#licence)
- [Crédits](#crédits)

---

## Fonctionnalités

- Génération d’un **site Web statique**
- Page d’accueil avec :
  - toutes les images,
  - triées du **plus récent au plus ancien**,
  - recherche textuelle instantanée,
  - filtres par type d’objet et catalogue
- **Clic sur l’image (page d’accueil) → page de l’objet**
- Pages objet individuelles avec :
  - image principale prédominante,
  - auteur et licence,
  - tableau des métadonnées de l’image,
  - tableau des caractéristiques astronomiques,
  - image astrométrique cliquable
- Enrichissement automatique via :
  - **SIMBAD**
  - **catalogue Messier (XLSX local)**
- Astrométrie optionnelle via **astrometry.net**
- Cache persistant pour :
  - SIMBAD
  - astrométrie (WCS + PNG)
- SEO :
  - sitemap.xml
  - robots.txt
  - JSON-LD (schema.org / ImageObject)

---

## Philosophie de navigation

La galerie adopte une structure claire et cohérente :

| Élément | Rôle |
|------|------|
| Page d’accueil | Découverte visuelle, exploration, filtrage |
| Page objet | Analyse scientifique, métadonnées, astrométrie |
| Image brute | Consultation ou téléchargement ponctuel |

### Navigation clé
- ✅ clic sur l’image de la page d’accueil → **page objet**
- ❌ plus de liens redondants sous les cartes
- 🔭 astrométrie accessible **uniquement sur la page objet**
- 📷 image HD accessible depuis la page objet

---

## Structure des données Seestar

Structure attendue (exemple) :

```
MyWorks/
  M 51/
    image_finale.jpg
    image_finale_thn.jpg
    Stacked_*.fit
  M 51_sub/      <- ignoré
  M 51-sub/      <- ignoré
  Altair/
    image.jpg
```

---

## Prérequis

### Système
- Windows 10 / 11

### Python
- Python **3.10+** recommandé

### Dépendances Python
```
pip install requests numpy matplotlib astropy pillow openpyxl
```

---

## Installation

```
git clone <repo>
cd GNU-Astro-Galery
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Utilisation

Depuis le dossier contenant `MyWorks` :

```
python generate_gallery.py
```

Le site est généré dans :

```
MyWorks/site/
```

---

## Catalogue Messier (XLSX)

Le script charge automatiquement un fichier Excel local nommé :

```
Objets Messiers..xlsx
```

Ce fichier doit contenir (au minimum) :
- Numéro Messier (M 1, M27, etc.)
- Type d’objet
- NGC / IC
- Constellation
- Magnitude
- Taille
- Distance (années-lumière)

Les données sont ajoutées automatiquement aux pages objet.

---

## Enrichissement via SIMBAD

- Le script interroge SIMBAD **à partir du nom du répertoire** (ex. `M 27`, `Altair`)
- Les résultats sont mis en cache local
- Informations typiques :
  - identifiant principal,
  - type astrophysique,
  - désignations,
  - mots-clés

---

## Pages objet

Chaque objet possède une page dédiée :

- Image principale prédominante
- **Auteur** : Steve Prud’Homme
- **Licence** : Creative Commons CC0 1.0
- Section **Métadonnées de l’image** :
  - date,
  - instrument,
  - filtre,
  - durée d’exposition,
  - résolution, etc.
- Section **Caractéristiques de l’objet** :
  - données SIMBAD,
  - données Messier (si applicable)
- Section **Astrométrie** :
  - aperçu réduit,
  - clic pour agrandir

---

## Astrométrie

### Optionnelle — via astrometry.net

Une clé API Nova est requise.

Configuration temporaire :
```
set NOVA_ASTROMETRY_API_KEY=VOTRE_CLE
```

Ou persistante :
```
setx NOVA_ASTROMETRY_API_KEY "VOTRE_CLE"
```

---

## Cache astrométrie

Les résultats sont mis en cache dans :

```
cache/astrometry/
```

- WCS FITS
- PNG astrométrique
- index JSON

Le cache évite les re-soumissions inutiles.

---

## Règles d’inclusion / exclusion

Inclus :
- fichiers `.jpg` finaux

Exclus :
- dossiers se terminant par `_sub` ou `-sub`
- fichiers `*_thn.jpg`

---

## SEO et données structurées

- JSON-LD `ImageObject` par page objet
- sitemap.xml automatique
- robots.txt automatique
- balises OpenGraph

---

## Dépannage

### Erreur WinError 5 (permissions)
- fermer les explorateurs ouverts sur `site/`
- supprimer le dossier `site/` puis relancer
- éviter les dossiers synchronisés (OneDrive)

### SIMBAD incomplet
- vérifier le nom du dossier
- vider le cache SIMBAD si nécessaire

---

## Sécurité et confidentialité

- Site 100 % statique
- Aucune donnée personnelle exposée
- Astrometry.net : images non publiques

---

## Publication

Le dossier `site/` peut être publié sur :
- GitHub Pages
- Netlify
- Cloudflare Pages
- serveur personnel

---

## Licence

Le **code** peut être distribué sous licence GNU (GPLv3 recommandée).  
Les **images** sont publiées sous :

> **Creative Commons CC0 1.0**

---

## Crédits

- AstroPy
- SIMBAD (CDS)
- astrometry.net
- Bootstrap 5
- Pillow
- OpenPyXL

---

**Auteur**  
Steve Prud’Homme
