# GNU Astro Galery

Galerie Web statique (HTML5/CSS3/Bootstrap 5) pour images du télescope intelligent **Seestar S50**.  
Le script parcourt votre répertoire **MyWorks**, collecte les images **JPG finales**, enrichit automatiquement les **tags** (SIMBAD + catalogue Messier), génère une **front page** triée du plus récent au plus vieux, des **pages par objet** soignées, et peut produire (optionnellement) une **image d’astrométrie** (grille RA/DEC) via **astrometry.net** avec **cache persistant**.

---

## Nouveautés (vX.Y)

### ✅ Page objet “premium”
Chaque objet a maintenant une page dédiée (Bootstrap 5) avec :
- **Image principale prédominante** (hero)
- **Auteur** : *Steve Prud’Homme*
- **Licence** : *Creative Commons CC0 1.0*
- Section **Métadonnées de l’image** (tableau)
- Section **Caractéristiques de l’objet** (tableau, SIMBAD + Messier XLSX)
- **Astrométrie** en aperçu (taille raisonnable) + **clic → agrandissement (modal)**

### ✅ SIMBAD plus fiable
- SIMBAD utilise le **nom du répertoire d’observation** (ex.: `M 27`, `Altair`) comme identifiant.
- Exclusion des dossiers finissant par **`_sub`** ou **`-sub`**.

### ✅ Enrichissement Messier via fichier XLSX
Si l’objet est de type **Messier** (`M1` ou `M 1`), le script lit un fichier Excel et ajoute :
- **Type** (ex.: nébuleuse planétaire, amas globulaire, galaxie…)
- **Nom NGC/IC**
- **Constellation**
- **Magnitude**
- **Taille**
- **Distance (al)**

### ✅ Cache persistant d’astrométrie
Évite de re-uploader/re-solve à chaque génération :
- cache dans `cache/astrometry/`
- index `cache/astrometry/index.json`
- réutilisation automatique de `*-wcs.fits` + `*-astrometry.png` si la source n’a pas changé

---

## Table des matières
- [Fonctionnalités](#fonctionnalités)
- [Structure des données Seestar (hypothèses)](#structure-des-données-seestar-hypothèses)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Catalogue Messier (XLSX)](#catalogue-messier-xlsx)
- [Pages objet](#pages-objet)
- [Astrométrie (optionnelle)](#astrométrie-optionnelle)
- [Cache astrométrie (persistant)](#cache-astrométrie-persistant)
- [Règles de découverte des images](#règles-de-découverte-des-images)
- [SEO / Données structurées (schema.org)](#seo--données-structurées-schemaorg)
- [Dépannage](#dépannage)
- [Sécurité & confidentialité](#sécurité--confidentialité)
- [Publication / Hébergement](#publication--hébergement)
- [Licence](#licence)
- [Crédits](#crédits)

---

## Fonctionnalités

- **Site statique** (aucun backend requis)
  - `index.html` avec **toutes les images** triées du plus récent au plus vieux
  - recherche instantanée + filtres (type d’objet, catalogue)
  - pages par objet (ex.: `gallery/m-51.html`)
- **Pages objet** :
  - image hero prédominante
  - auteur/licence visibles
  - 2 tableaux : **Métadonnées** et **Caractéristiques**
  - image **astrométrique cliquable** (modal)
- **Bootstrap 5** (responsive)
- **SEO / découvrabilité** :
  - `sitemap.xml`, `robots.txt`
  - balises OpenGraph / Twitter Cards
  - **JSON-LD schema.org** (`ImageObject`) par objet
- **Règles Seestar respectées** :
  - ignore les répertoires finissant par **`_sub`** ou **`-sub`**
  - ignore les fichiers `*_thn.jpg`
  - traite l’image JPG finale du répertoire “non-sub”
- **Tags automatiques** :
  - enrichissement via **SIMBAD**
  - cache local de résultats SIMBAD
- **Enrichissement Messier** :
  - lecture d’un catalogue XLSX local (voir section dédiée)
  - ajout type, NGC/IC, constellation, magnitude, taille, distance
- **Astrométrie (optionnelle)** :
  - plate-solve via **nova.astrometry.net**
  - rendu local d’un PNG “grille RA/DEC”
  - fallback JPG si FITS sans image 2D
  - **cache persistant** pour accélérer les relances

---

## Structure des données Seestar (hypothèses)

```
MyWorks/
  M 51/
    ... (fichiers)
    image_finale.jpg
    image_finale_thn.jpg (optionnel)
    Stacked_...fit / Stacked_...fits (optionnel mais recommandé)
  M 51_sub/      <- ignoré
  M 51-sub/      <- ignoré
  IC 342/
    ...
```

---

## Prérequis

### Système
- Windows 10/11

### Python
- Python **3.10+** recommandé :
```powershell
python --version
```

### Dépendances
- `requests`
- `numpy`
- `matplotlib`
- `astropy`
- `pillow`
- `openpyxl` (requis pour le XLSX Messier)

Installation :
```powershell
pip install requests numpy matplotlib astropy pillow openpyxl
```

---

## Installation

```powershell
git clone <votre-repo>
cd GNU-Astro-Galery
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install requests numpy matplotlib astropy pillow openpyxl
```

---

## Configuration

### 1) Dossier MyWorks
Exécutez depuis le dossier qui contient vos répertoires d’objets :

```powershell
cd F:\MyWorks
python gnu_astro_galery.py
```

### 2) BASE_URL (si vous publiez)
Dans le script :
```python
BASE_URL = "https://example.com/seestar"
```
- en local : non bloquant
- en ligne : mettez l’URL réelle (sinon OG/sitemap pointent vers une URL fictive)

### 3) Auteur + licence
Dans le script :
```python
CREATOR_NAME = "Steve Prud’Homme"
IMAGE_LICENSE = "Creative Commons CC0 1.0"
```

---

## Catalogue Messier (XLSX)

### Fichier attendu
Placez ce fichier **à côté du script** (ou dans le dossier `MyWorks`) :

- **`Objets Messiers..xlsx`**

Le script cherche dans l’ordre :
1) à côté du script  
2) dans `MyWorks`  
3) fallback : premier `*.xlsx` contenant “Messier” dans le nom

### Champs ajoutés automatiquement
Pour un objet `M1` / `M 1` / `m001` :
- `messier` (ex. `M 27`)
- `ngc` (ex. `NGC 6853`)
- `constellation`
- `magnitude`
- `size`
- `distance_ly` (années-lumière)
- `messier_type`

Ces champs sont écrits dans :
- `site/data/images.json`
- et affichés sur la page objet (section **Caractéristiques de l’objet**)

---

## Pages objet

Les pages objet sont générées dans :
```
site/gallery/<slug>.html
```

Elles contiennent :
- **Hero image** (dominante, responsive)
- **Auteur** + **Licence**
- Tableau **Métadonnées de l’image**
- Tableau **Caractéristiques de l’objet**
  - infos SIMBAD (main_id, otype, otype_txt, etc.)
  - infos Messier (si applicable)
- **Astrométrie** en petit aperçu + **modal** au clic

---

## Astrométrie (optionnelle)

### Obtenir une clé API Nova (astrometry.net)
1) créer un compte astrometry.net (Nova)
2) récupérer la **API Key**
3) configurer la variable d’environnement :

Session PowerShell :
```powershell
$env:NOVA_ASTROMETRY_API_KEY="VOTRE_CLE_ICI"
python gnu_astro_galery.py
```

Persistant :
```powershell
setx NOVA_ASTROMETRY_API_KEY "VOTRE_CLE_ICI"
```
Puis **rouvrir** PowerShell.

### Notes importantes
- Upload configuré en **non-public** (`publicly_visible="n"`)
- Si le FITS ne contient pas d’image 2D exploitable, le rendu PNG utilise le **JPG** local

---

## Cache astrométrie (persistant)

Stockage :
- `cache/astrometry/index.json`
- `cache/astrometry/<cache-key>-wcs.fits`
- `cache/astrometry/<cache-key>-astrometry.png`

Le cache est réutilisé si :
- `wcs.fits` + `astrometry.png` existent
- ET la source n’a pas changé (empreinte **taille + mtime**)

> Le cache est **hors de `site/`** pour survivre aux régénérations.

---

## Règles de découverte des images

Inclus :
- tous les `*.jpg` dans les dossiers d’objets

Exclus :
- dossiers finissant par `_sub` ou `-sub`
- fichiers `*_thn.jpg`

---

## SEO / Données structurées (schema.org)

- JSON-LD `ImageObject` injecté dans chaque page objet
- `sitemap.xml` généré automatiquement
- `robots.txt` généré automatiquement

---

## Dépannage

### “Tags SIMBAD manquants”
- Vérifier que le nom du dossier est propre (`Altair`, `M 27`, etc.)
- Purger le cache :
  - `cache/object_info.json`

### “Le XLSX Messier n’est pas lu”
- vérifier le nom : `Objets Messiers..xlsx`
- vérifier `openpyxl` :
```powershell
pip show openpyxl
```

### “Astrométrie relancée tout le temps”
- vérifier que `cache/astrometry/` n’est pas supprimé
- si vos fichiers FITS/JPG sont réécrits souvent, le `mtime` change → cache invalidé

---

## Sécurité & confidentialité

- Site généré : **local et statique**
- SIMBAD : requêtes metadata (identifiants uniquement)
- Astrometry.net : upload FITS si activé (clé Nova), non-public

---

## Publication / Hébergement

Copiez le dossier `site/` vers :
- GitHub Pages
- Netlify
- Cloudflare Pages
- NAS / serveur perso

---

## Licence

Choisissez une licence pour le code :
- GPLv3 (esprit “GNU”)
- MIT (permissif)

Ajoutez `LICENSE`.

---

## Crédits

- Bootstrap 5
- AstroPy (FITS/WCS)
- Pillow
- OpenPyXL
- SIMBAD (CDS)
- Astrometry.net (Nova)
