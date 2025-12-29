# GNU Astro Galery

Galerie Web statique (HTML5/CSS3/Bootstrap 5) pour images du télescope intelligent **Seestar S50**.  
Le script parcourt votre répertoire **MyWorks**, collecte les images **JPG finales**, extrait des métadonnées (quand disponibles), enrichit automatiquement les **tags** (ex.: galaxie, amas globulaire, nébuleuse), génère une **front page** triée du plus récent au plus vieux, des **pages par objet**, et peut produire (optionnellement) une **image d’astrométrie** (grille RA/DEC) via **astrometry.net**.

---

## Nouveauté (vX.Y) — Correction SIMBAD (tags manquants)
**SIMBAD utilise maintenant le nom du répertoire d’observation** (ex.: `M 27`, `Altair`) comme identifiant, plutôt que le nom du fichier ou `OBJECT` du FITS, afin d’éviter les suffixes du type `LP`, `IRCut`, etc.  
Les dossiers terminant par **`_sub`** ou **`-sub`** sont exclus.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Structure des données Seestar (hypothèses)](#structure-des-données-seestar-hypothèses)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Règles de découverte des images](#règles-de-découverte-des-images)
- [Tags automatiques (SIMBAD)](#tags-automatiques-simbad)
- [Astrométrie (optionnelle)](#astrométrie-optionnelle)
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
- **Astrométrie (optionnelle)** :
  - plate-solve via **nova.astrometry.net**
  - rendu local d’un PNG “grille RA/DEC” pour la page objet
  - fallback automatique si le FITS n’a pas d’image 2D : utilisation du **JPG** local

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

Installer :
```powershell
pip install requests numpy matplotlib astropy pillow
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
pip install requests numpy matplotlib astropy pillow
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

## Utilisation

Depuis le dossier MyWorks :

```powershell
python gnu_astro_galery.py
```

Le script :
1. détecte toutes les images JPG finales (hors `_sub`/`-sub`, hors `_thn.jpg`)
2. enrichit tags/catalogue/type d’objet
3. génère la galerie dans `.\site`
4. (optionnel) lance plate-solve et produit `site\astrometry\*.png`

Ouvrir la galerie :
- double-cliquez `site\index.html`

---

## Règles de découverte des images

Le script **inclut** :
- tous les fichiers `*.jpg` dans les dossiers d’objets

Le script **exclut** :
- tout ce qui se trouve dans un dossier finissant par `_sub` ou `-sub`
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

### “Login Nova impossible / réponse non-JSON”
- Vérifiez `NOVA_ASTROMETRY_API_KEY`
- Relancez dans PowerShell avec :
```powershell
echo $env:NOVA_ASTROMETRY_API_KEY
```

### “PNG astrométrie non généré”
- Si le FITS ne contient pas une image 2D, le script bascule sur le JPG
- Consultez les warnings dans la console

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
- SIMBAD (CDS) pour l’enrichissement des objets
- Astrometry.net (Nova) pour le plate-solve
