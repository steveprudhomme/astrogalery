# GNU Astro Galery

Galerie Web statique (HTML5/CSS3/Bootstrap 5) pour images du télescope intelligent **Seestar S50**.  
Le script parcourt votre répertoire **MyWorks**, collecte les images **JPG finales**, extrait des métadonnées (quand disponibles), enrichit automatiquement les **tags** (ex.: galaxie, amas globulaire, nébuleuse), génère une **front page** triée du plus récent au plus vieux, des **pages par objet**, et peut produire (optionnellement) une **image d’astrométrie** (grille RA/DEC) via **astrometry.net**.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Structure des données Seestar (hypothèses)](#structure-des-données-seestar-hypothèses)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Sortie générée (arborescence du site)](#sortie-générée-arborescence-du-site)
- [Tags automatiques](#tags-automatiques)
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
  - ignore les répertoires terminant par **`_sub`** (ex.: `M 77_sub`)
  - ignore les fichiers `*_thn.jpg`
  - traite l’image JPG finale dans le répertoire “non-sub”
- **Tags automatiques** :
  - heuristique locale + enrichissement en ligne via **SIMBAD** (stable et populaire)
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

### Règles appliquées

- ✅ Traite **seulement** les JPG **hors** dossiers `*_sub`
- ✅ Ignore tout JPG finissant par `_thn.jpg`
- ✅ Copie la vignette si elle existe : `nom_thn.jpg` (sinon, la grande image sert aussi de vignette)

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
- `pillow` (lecture JPG fallback)
- (optionnel) rien de plus pour Bootstrap (CDN)

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

### 1) Positionnement du script

Placez le script `gnu_astro_galery.py` dans le dossier **MyWorks** (ou exécutez-le depuis MyWorks) car il scanne **le répertoire courant**.

Exemple :
```powershell
cd F:\MyWorks
python gnu_astro_galery.py
```

### 2) BASE_URL (si vous publiez)

Dans le script, modifiez :
```python
BASE_URL = "https://example.com/seestar"
```

- Si usage local seulement : pas critique (OpenGraph/sitemap auront un URL fictif)
- Si publication : mettre votre URL réelle (GitHub Pages, domaine perso, etc.)

### 3) Clé API astrometry.net (optionnelle)

Si vous voulez la génération des images d’astrométrie :

#### Créer / récupérer votre clé API
1. Créez un compte sur astrometry.net (Nova)
2. Dans votre compte, récupérez la **API Key** (section “API Key” / “Nova”)

#### Définir la variable d’environnement sous Windows (PowerShell)

Pour la session courante :
```powershell
$env:NOVA_ASTROMETRY_API_KEY="VOTRE_CLE_ICI"
python gnu_astro_galery.py
```

Pour définir de façon persistante (utilisateur courant) :
```powershell
setx NOVA_ASTROMETRY_API_KEY "VOTRE_CLE_ICI"
```

Puis **rouvrir** PowerShell.

---

## Utilisation

Depuis le dossier MyWorks :

```powershell
python gnu_astro_galery.py
```

Le script :
1. détecte toutes les images JPG finales (hors `_sub`, hors `_thn.jpg`)
2. enrichit tags/catalogue/type d’objet
3. génère la galerie dans `.\site`
4. (optionnel) lance plate-solve et produit `site\astrometry\*.png`

### Ouvrir la galerie
- Double-cliquez `site\index.html`  
ou
- Glissez-déposez `index.html` dans votre navigateur

---

## Sortie générée (arborescence du site)

```
site/
  index.html
  sitemap.xml
  robots.txt
  assets/
    css/styles.css
    js/app.js
  data/
    images.json
    img/
      <images copiées ici>
    solved/
      <WCS header-only téléchargés>
  gallery/
    <une page par objet>.html
  astrometry/
    <PNGs RA/DEC>
```

---

## Tags automatiques

### Comment ça marche

- Extraction du nom d’objet (via header FITS `OBJECT` quand disponible, sinon nom de dossier)
- Déduction de catalogue : Messier, NGC, IC, Sharpless, etc.
- Enrichissement via **SIMBAD** (CDS) :
  - récupère `otype` / `otype_txt`
  - mappe vers tags (ex.: `GlC` → **amas globulaire**)
- Cache local :
  - écrit `cache/object_info.json`
  - accélère les exécutions suivantes

### Exemples de tags
- `galaxie`, `galaxie spirale`, `amas globulaire`, `nébuleuse`, `nébuleuse planétaire`, etc.

---

## Astrométrie (optionnelle)

### Principe
- Upload du FITS sur astrometry.net (Nova)
- Téléchargement du **WCS header-only** via `wcs_file/<jobid>`
- Rendu local d’un PNG (matplotlib + astropy.wcs) :
  - image = FITS local si lisible
  - sinon **fallback sur le JPG** (pour éviter les FITS “non-image”)

### Limites connues
- Si le JPG n’est pas parfaitement aligné (resize/crop) par rapport au FITS uploadé, la grille peut être légèrement décalée.
- Le Seestar S50 n’offre pas toujours un WCS fiable en local, d’où l’usage du plate-solve en ligne.

---

## Pourquoi la recherche fonctionne en local

Le fichier `index.html` contient les données `images.json` **inlinées** dans une balise :

```html
<script id="images-data" type="application/json"> ... </script>
```

✅ Résultat : pas besoin de serveur, pas de blocage CORS / fetch en `file:///`.

---

## Dépannage

### 1) “Aucun JPG final trouvé”
- Vérifiez que vous exécutez le script dans le bon dossier (ex.: `F:\MyWorks`)
- Vérifiez qu’il y a bien des `.jpg` non `_thn` dans des dossiers non `_sub`

### 2) SIMBAD ne retourne rien / erreur réseau
- Le script continue sans tags SIMBAD
- Vérifiez votre connexion Internet
- Relancez : le cache aide à limiter les requêtes

### 3) Astrométrie: login impossible / réponse non-JSON
- Vérifiez la variable `NOVA_ASTROMETRY_API_KEY`
- Vérifiez que la clé est valide
- Essayez dans PowerShell :
```powershell
echo $env:NOVA_ASTROMETRY_API_KEY
```

### 4) Astrométrie: PNG non généré
Ca arrive si :
- ni le FITS ni le JPG ne peut être lu (rare)
- le WCS téléchargé est incomplet / mismatch

Le script journalise alors l’avertissement correspondant.

---

## Sécurité & confidentialité

- Le site généré est **local** et statique.
- Pour l’astrométrie, le script **envoie des FITS** à astrometry.net (Nova) pour résoudre le champ.
- Par défaut, l’upload est configuré en **non-public** (`publicly_visible="n"`), mais l’image est quand même transmise au service pour calcul.

---

## Publication / Hébergement

Options simples :
- GitHub Pages (statique)
- Netlify
- Cloudflare Pages
- Serveur perso / NAS

Copiez simplement le contenu du dossier `site/`.

---

## Licence

**GNU Astro Galery** 

- GPLv3

> Ajoutez un fichier `LICENSE` à la racine du projet.

---

## Crédits

- Bootstrap 5 (CDN)
- AstroPy / FITS / WCS
- SIMBAD (CDS) pour l’enrichissement des objets
- Astrometry.net (Nova) pour le plate-solve

---
```
