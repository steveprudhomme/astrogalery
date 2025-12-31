# CHANGELOG — GNU Astro Galery

## [0.8.0] — 2025‑09

### Ajouts
- Bloc météo / conditions d’observation sur les pages objet
- Extraction DATE-OBS / SITELAT / SITELONG depuis les FITS Seestar
- Récupération météo via Open‑Meteo (archive API)
- Cache local météo
- Indicateur de progression météo en console

### Correctifs
- Correction critique : conservation des chemins FITS/JPG internes jusqu’à la génération des pages objet
- Correction des erreurs d’indentation bloquantes
- Correction du lien FITS → page objet (météo et astrométrie)
- Ouverture FITS plus robuste (`ignore_missing_simple=True`)

### Technique
- Module météo isolé (`space_weather.py`)
- Séparation données internes / données publiques
- Aucune régression sur la starmap, l’astrométrie ou les catalogues
