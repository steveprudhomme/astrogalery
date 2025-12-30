# CHANGELOG
Tous les changements notables de **GNU Astro Galery** sont documentés dans ce fichier.

Le projet suit l’esprit de **Keep a Changelog** avec une numérotation de version interne propre au projet.

---

## [0.8.0] – 2025-09-30

### Ajouté
- Génération d’une **page objet centrale et documentaire**
- Ajout d’un **bloc Météo & conditions d’observation** basé sur :
  - `DATE-OBS`, `SITELAT`, `SITELONG` (FITS)
  - données météo historiques open source
- Génération de **cartes stellaires de type atlas** :
  - centrées sur l’objet observé
  - affichage des objets Messier dans le champ
  - affichage des objets issus de `objetsdivers.xlsx` (magnitude ≤ 6)
- Support d’un **catalogue XLSX multi-feuilles** pour les objets divers
- Mise en place d’un **cache persistant** pour :
  - SIMBAD
  - astrométrie
  - cartes stellaires
  - météo d’observation
- Ajout systématique des métadonnées :
  - Auteur : Steve Prud’Homme
  - Licence : Creative Commons CC0 1.0
- Intégration complète du SEO :
  - OpenGraph
  - JSON-LD (ImageObject)
  - sitemap.xml
  - robots.txt

### Modifié
- Navigation :
  - clic sur une image mène directement à la **page objet**
  - suppression des liens redondants sous les vignettes
- Pages objet :
  - image principale dominante
  - sections normalisées et hiérarchisées
- Enrichissement astronomique :
  - priorité au **nom du répertoire** pour SIMBAD
  - priorité aux données Messier locales sur SIMBAD
- Cartes stellaires :
  - filtrage des identifiants techniques (Gaia, ZTF, TYC, etc.)
  - priorité aux objets visibles et pédagogiques

### Corrigé
- Positionnement incorrect des labels (regroupés au centre)
- Génération des PNG astrométriques lorsque seul le WCS est disponible
- Exclusion incorrecte de certains dossiers :
  - `_sub`
  - `-sub`
- Problèmes de permissions Windows lors de la création des dossiers
- Erreurs liées aux métadonnées OpenGraph manquantes
- Normalisation automatique des coordonnées célestes invalides (secondes = 60)

---

## [0.7.x] – 2025-09

### Ajouté
- Cache local pour les requêtes SIMBAD
- Première intégration du catalogue Messier (XLSX)
- Astrométrie via astrometry.net (optionnelle)

### Modifié
- Amélioration de la détection automatique :
  - type d’objet
  - catalogue
  - nom principal

### Corrigé
- Exclusion des fichiers `*_thn.jpg`
- Exclusion correcte des dossiers `_sub`

---

## [0.6.x] – 2025-08

### Ajouté
- Recherche textuelle dynamique côté client
- Filtres par type d’objet et catalogue
- Génération automatique de sitemap.xml et robots.txt

---

## [0.5.x] – 2025-08

### Ajouté
- Génération automatique d’une galerie HTML statique
- Intégration de Bootstrap 5

---

## [0.4.x] – 2025-07

### Ajouté
- Extraction des métadonnées FITS
- Structuration initiale des pages objet

---

## [0.3.x] – 2025-07

### Ajouté
- Scan récursif du répertoire racine
- Détection des images finales Seestar S50

---

## [0.2.x] – 2025-07

### Ajouté
- Organisation par répertoires d’objets

---

## [0.1.0] – 2025-07-15

### Ajouté
- Prototype initial de génération de galerie
- Architecture générale du projet

---

**Auteur**  
Steve Prud’Homme
