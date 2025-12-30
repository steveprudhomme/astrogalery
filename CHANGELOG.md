# CHANGELOG

Tous les changements notables de **GNU Astro Galery** sont documentés dans ce fichier.

---

## [0.8.0] – 2025-09

### Ajouté
- Génération des pages objet complètes et documentaires
- Intégration des catalogues :
  - Messier (XLSX)
  - objets divers (XLSX multi-feuilles)
- Cartes stellaires locales (type atlas)
- Astrométrie optionnelle avec mise en cache
- **Intégration du module externe `space_weather.py`**
  - génération des conditions d’observation depuis les en-têtes FITS
  - module importé dynamiquement (non exécutable seul)
- SEO complet :
  - OpenGraph
  - JSON-LD
  - sitemap.xml

### Modifié
- Architecture :
  - clarification du rôle du script principal et des modules
- Navigation :
  - clic sur l’image mène directement à la page objet

### Corrigé
- Exclusion correcte des dossiers `_sub` et `-sub`
- Exclusion des miniatures `_thn.jpg`
- Corrections de positionnement des labels sur les cartes stellaires

---
