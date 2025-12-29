# GNU Astro Galery

Galerie Web statique (HTML5/CSS3/Bootstrap 5) pour images du télescope intelligent **Seestar S50**.  
Le script parcourt votre répertoire **MyWorks**, collecte les images **JPG finales**, extrait des métadonnées (quand disponibles), enrichit automatiquement les **tags** (ex.: galaxie, amas globulaire, nébuleuse), génère une **front page** triée du plus récent au plus vieux, des **pages par objet**, et peut produire (optionnellement) une **image d’astrométrie** (grille RA/DEC) via **astrometry.net**.

---

## Nouveautés (vX.Y)

### ✅ SIMBAD plus fiable
- **SIMBAD utilise le nom du répertoire d’observation** (ex.: `M 27`, `Altair`) comme identifiant, plutôt que le nom de fichier ou `OBJECT` du FITS.
- Exclusion systématique des dossiers finissant par **`_sub`** ou **`-sub`**.

### ✅ Enrichissement Messier via fichier XLSX
Si l’objet est de type **Messier** (`M1` ou `M 1`), le script lit un **catalogue Excel** placé à côté du script et ajoute automatiquement :
- **Type** (ex.: nébuleuse planétaire, amas globulaire, galaxie…)
- **Nom NGC/IC** (si présent)
- **Constellation**
- **Magnitude**
- **Taille**
- **Distance (al)**

Fichier attendu : **`Objets Messiers..xlsx`**.

### ✅ Cache persistant d’astrométrie (nouveau)
Pour éviter de **ré-uploader**, **re-solve** et **re-télécharger** à chaque génération :

- Les fichiers astrométriques sont désormais mis en cache dans :
  - `cache/astrometry/`
  - index : `cache/astrometry/index.json`
- Le script **réutilise automatiquement** :
  - le WCS header-only `*-wcs.fits`
  - le PNG `*-astrometry.png`
- Le solve ne se relance que si le FITS/JPG source a changé (taille ou date modifiée).

> Important : comme `site/` est régénéré à chaque exécution, ce cache **est volontairement hors de `site/`** pour survivre aux runs.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Structure des données Seestar (hypothèses)](#structure-des-données-seestar-hypothèses)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Catalogue Messier (XLSX)](#catalogue-messier-xlsx)
- [Astrométrie (optionnelle)](#astrométrie-optionnelle)
- [Cache astrométrie (persistant)](#cache-astrométrie-persistant)
- [Règles de découverte des images](#règles-de-découverte-des-images)
- [Tags automatiques (SIMBAD)](#tags-automatiques-simbad)
- [Pourquoi la recherche fonctionne en local](#pourquoi-la-recherche-fonctionne-en-local)
- [Dépannage](#dépannage)
- [Sécurité & confidentialité](#sécurité--confidentialité)
- [Publication / Hébergement](#publication--hébergement)
- [Licence](#licence)
- [Crédits](#crédits)

---

## Fonctionnalités

- **Site statique** (aucun backend requis) :
  - `index.html` (front page) avec **toutes les images** triées du **plus récent au plus vieux**
  - recherche instantanée + filtres (type d’objet, catalogue)
  - pages par objet (ex.: `gallery/m-51.html`)
- **Bootstrap 5** (responsive, propre, rapide).
- **SEO / découvrabilité** :
  - `sitemap.xml`, `robots.txt`
  - balises OpenGraph / Twitter Cards
  - **schema.org JSON-LD** (`ImageObject`) par objet
- **Règles Seestar respectées** :
  - ignore les répertoires terminant par **`_sub`** ou **`-sub`**
  - ignore les fichiers `*_thn.jpg`
  - traite l’image JPG finale dans le répertoire “non-sub”
- **Tags automatiques** :
  - heuristique locale + enrichissement en ligne via **SIMBAD** (standard stable et très utilisé)
  - cache local pour accélérer les exécutions suivantes
- **Enrichissement Messier** :
  - lecture d’un catalogue XLSX local (voir section dédiée)
  - ajout du type, NGC/IC, constellation, magnitude, taille, distance
- **Astrométrie (optionnelle)** :
  - plate-solve via **nova.astrometry.net**
  - rendu local d’un PNG “grille RA/DEC” pour la page objet
  - fallback automatique si le FITS n’a pas d’image 2D : utilisation du **JPG** local
  - **cache persistant** (nouveau) pour éviter les re-solves

---

## Structure des données Seestar (hypothèses)

Le script s’attend à une structure de type :

```
MyWorks/
  M 51/
    ... (fichiers)
    image_finale.jpg
    (optionnel) image_finale_thn.jpg
    Stacked_...fit / Stacked_...fits
  M 51_sub/      <- ignoré
  M 51-sub/      <- ignoré
  IC 342/
    ...
```

---

## Prérequis

### Système
- Windows 10/11 (natif)

### Python
- Python **3.10+** recommandé  
  Vérifier :
```powershell
python --version
```

### Dépendances Python
- `requests`
- `numpy`
- `matplotlib`
- `astropy`
- `pillow`
- `openpyxl` (**requis pour le XLSX Messier**)

Installer :
```powershell
pip install requests numpy matplotlib astropy pillow openpyxl
```

---

## Installation

1) **Cloner / copier** le projet dans un dossier de travail :
```powershell
git clone <votre-repo-ou-dossier>
cd GNU-Astro-Galery
```

2) (Recommandé) créer un environnement virtuel :
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3) Installer les dépendances :
```powershell
pip install -U pip
pip install requests numpy matplotlib astropy pillow openpyxl
```

---

## Configuration

### 1) Dossier MyWorks
Exécutez le script depuis votre répertoire **MyWorks** (celui qui contient les dossiers d’objets) :

```powershell
cd F:\MyWorks
python gnu_astro_galery.py
```

### 2) BASE_URL (si vous publiez)
Dans le script, modifiez :
```python
BASE_URL = "https://example.com/seestar"
```

- usage local : non bloquant
- publication : mettez l’URL réelle (GitHub Pages, domaine perso, etc.)

### 3) Clé API astrometry.net (optionnelle)
Si vous voulez la génération des images d’astrométrie :

#### Récupérer votre clé API
1. Créez un compte sur astrometry.net (Nova)
2. Dans votre compte, récupérez la **API Key**

#### Définir la variable d’environnement (PowerShell)
Pour la session courante :
```powershell
$env:NOVA_ASTROMETRY_API_KEY="VOTRE_CLE_ICI"
python gnu_astro_galery.py
```

Pour définir de façon persistante :
```powershell
setx NOVA_ASTROMETRY_API_KEY "VOTRE_CLE_ICI"
```
Puis **rouvrez** PowerShell.

---

## Catalogue Messier (XLSX)

### Fichier attendu
Placez le fichier suivant **dans le même dossier que le script** (ou dans le dossier courant) :

- **`Objets Messiers..xlsx`**

Le script tentera :
1) `./Objets Messiers..xlsx` (à côté du script)  
2) `MyWorks/Objets Messiers..xlsx` (dossier courant)  
3) sinon, le premier `*.xlsx` contenant “Messier” dans le nom (fallback)

### Ce qui est ajouté automatiquement (pour `M1` / `M 1`, etc.)
- `messier` (ex. `M 27`)
- `ngc` (ex. `NGC 6853`)
- `constellation`
- `magnitude`
- `size`
- `distance_ly` (distance en années-lumière)
- `messier_type` (type texte du catalogue)

Ces champs sont :
- intégrés dans `data/images.json`
- utilisables par la recherche et les filtres
- affichés sur la page objet et/ou dans la carte (selon la version)

> Note : certaines magnitudes dans l’Excel peuvent être interprétées comme dates (Excel).  
> Le script corrige cela automatiquement (ex.: `2025-04-08` → `8.4`).

---

## Astrométrie (optionnelle)

### Principe
- Upload du FITS sur astrometry.net (Nova)
- Téléchargement du **WCS header-only** via `wcs_file/<jobid>`
- Rendu local d’un PNG (matplotlib + astropy.wcs)
  - image = FITS local si lisible
  - sinon fallback sur le **JPG** local

### Confidentialité
L’upload est configuré en **non-public** (`publicly_visible="n"`), mais le fichier est transmis au service pour calcul.

---

## Cache astrométrie (persistant)

### Où sont stockés les fichiers ?
- `cache/astrometry/index.json` : index (cache-key → fingerprint)
- `cache/astrometry/<cache-key>-wcs.fits` : WCS header-only
- `cache/astrometry/<cache-key>-astrometry.png` : rendu PNG

### Quand le script réutilise le cache ?
Le cache est utilisé si :
- le couple `(wcs.fits + astrometry.png)` existe
- ET si le fichier source (FITS/JPG) n’a pas changé (fingerprint basé sur taille + mtime)

Dans ce cas :
- **aucun upload Nova**
- **aucun solve**
- **aucun re-téléchargement**
- le script copie simplement les fichiers vers `site/` pour les pages objets

---

## Règles de découverte des images

Le script **inclut** :
- tous les fichiers `*.jpg` dans les dossiers d’objets

Le script **exclut** :
- tout ce qui se trouve dans un dossier finissant par `_sub` **ou** `-sub`
- tout fichier finissant par `_thn.jpg` (miniatures Seestar)

---

## Tags automatiques (SIMBAD)

### Identifiant envoyé à SIMBAD (important)
Pour éviter les échecs de résolution (ex.: `M 27 LP`, `Altair IRCUT`, etc.) :

✅ **Le script envoie à SIMBAD le nom du dossier de l’objet** (ex.: `M 27`, `Altair`, `IC 342`)  
❌ Il n’utilise pas le nom de fichier, ni les suffixes du FITS (`OBJECT`) pour l’identification SIMBAD.

Les dossiers finissant par `_sub` ou `-sub` sont exclus.

### Cache local
Les réponses SIMBAD sont mises en cache dans :
```
cache/object_info.json
```
Cela accélère les relances et limite les requêtes.

---

## Pourquoi la recherche fonctionne en local

Les données `images.json` sont **inlinées** dans `index.html` via :

```html
<script id="images-data" type="application/json"> ... </script>
```

➡️ Cela évite les problèmes de `fetch()` en `file:///` (CORS / restrictions navigateur).

---

## Dépannage

### “Tags manquants sur des objets connus (ex.: M 27, Altair)”
- Vérifiez que l’objet a bien un dossier nommé proprement (`M 27`, `Altair`, etc.)
- Vérifiez le cache : supprimez `cache/object_info.json` et relancez si besoin

### “Le fichier Messier XLSX n’est pas lu”
- Vérifiez le nom exact : `Objets Messiers..xlsx`
- Assurez-vous qu’il est à côté du script ou dans `MyWorks`
- Vérifiez la dépendance :
```powershell
pip show openpyxl
```

### “Astrométrie relancée à chaque run”
- Vérifiez que `cache/astrometry/` n’est pas supprimé
- Vérifiez que les fichiers source FITS/JPG ne sont pas réécrits automatiquement par un autre logiciel
- Supprimez `cache/astrometry/index.json` si vous voulez forcer une reconstruction

---

## Sécurité & confidentialité

- Le site généré est **local** et statique.
- SIMBAD : requêtes de métadonnées (identifiants d’objets uniquement).
- Astrometry.net : envoi de FITS uniquement si l’option est activée (clé Nova fournie).

---

## Publication / Hébergement

Options :
- GitHub Pages
- Netlify
- Cloudflare Pages
- NAS / serveur perso

Copiez simplement le contenu du dossier `site/`.

---

## Licence

Choisissez une licence avant publication :
- GPLv3 (esprit “GNU”)
- MIT (permissif)

Ajoutez un fichier `LICENSE`.

---

## Crédits

- Bootstrap 5 (CDN)
- AstroPy / FITS / WCS
- Pillow
- OpenPyXL
- SIMBAD (CDS) pour l’enrichissement des objets
- Astrometry.net (Nova) pour le plate-solve
````
