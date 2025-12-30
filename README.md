# GNU Astro Galery
**Version : 0.8.0**

**GNU Astro Galery** est un générateur de galerie Web statique (HTML5 / CSS3 / Bootstrap 5) destiné aux images d’astrophotographie, initialement produites avec le **télescope intelligent Seestar S50**, mais conçu pour rester générique et extensible.

Le projet vise à produire une galerie :
- esthétique et moderne,
- scientifiquement documentée,
- totalement statique (aucun backend requis),
- facilement publiable (GitHub Pages, serveur Web, NAS),
- centrée sur la **page objet** comme unité principale de navigation.

---

## Architecture générale

- **generate_gallery.py**  
  Script principal (point d’entrée). Il orchestre :
  - le scan des images et FITS,
  - l’enrichissement astronomique (SIMBAD, catalogues),
  - la génération HTML,
  - l’appel aux modules spécialisés.

- **space_weather.py**  
  Module externe importé dynamiquement par `generate_gallery.py`.  
  Il **ne doit jamais être exécuté seul**.  
  Il fournit le bloc *Météo & conditions d’observation* à partir des en-têtes FITS.

---

## Fonctionnalités principales

- Génération complète d’un **site Web statique**
- Page d’accueil :
  - toutes les images détectées
  - tri chronologique
  - recherche textuelle instantanée
  - filtres dynamiques
- Pages objet :
  - image principale dominante
  - métadonnées FITS complètes
  - caractéristiques astronomiques
  - astrométrie
  - carte stellaire (atlas)
  - **conditions d’observation (module météo)**

---

## Météo spatiale et conditions d’observation

Le bloc météo est généré automatiquement via le module `space_weather.py` à partir des champs FITS suivants :

- `DATE-OBS`
- `SITELAT`
- `SITELONG`

Données actuellement prises en charge :
- température
- humidité
- pression atmosphérique
- direction et vitesse du vent

Les données sont issues de services météo open source et mises en cache localement.

---

## Prérequis

- Python 3.10+
- Bibliothèques principales :
  - astropy
  - astroquery
  - numpy
  - pandas
  - matplotlib
  - pillow
  - requests
  - openpyxl

---

## Utilisation

```bash
python generate_gallery.py
```

Un seul script doit être lancé.  
Les modules (ex. `space_weather.py`) sont appelés automatiquement.

---

## Licence

- Code : GNU GPL v3
- Images : Creative Commons CC0 1.0

---

## Auteur

**Steve Prud’Homme**
