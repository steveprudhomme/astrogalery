# Changelog
Tous les changements notables de **GNU Astro Galery** sont documentés dans ce fichier.

Le format suit l’esprit de **Keep a Changelog**, avec une numérotation de version interne au projet.

---

## [00.00.07] – 2025-09-28

### Ajouté
- Génération de **cartes stellaires de type atlas** sur les pages objet
- Affichage sur les cartes :
  - de l’objet cible,
  - des **objets Messier présents dans le champ**,
  - des objets issus de `objetsdivers.xlsx` avec **magnitude ≤ 6**
- Support d’un **catalogue XLSX multi-onglets** pour les objets divers
- Filtrage intelligent des labels :
  - exclusion des identifiants techniques (Gaia, ZTF, TYC, etc.)
  - priorité aux objets astronomiques pertinents
- Ajout d’un **système de cache** pour :
  - SIMBAD,
  - astrométrie,
  - cartes stellaires
- Ajout des **métadonnées complètes** sur les pages objet :
  - auteur (Steve Prud’Homme)
  - licence (Creative Commons CC0 1.0)

### Modifié
- Navigation :
  - clic sur une image de la page d’accueil mène directement à la **page objet**
  - suppression des liens redondants sous les vignettes
- Mise en page des pages objet :
  - image principale dominante
  - sections clairement structurées (Métadonnées, Caractéristiques, Astrométrie, Carte)
- Enrichissement des objets :
  - utilisation prioritaire du **nom du répertoire** pour les requêtes SIMBAD
- Normalisation des coordonnées célestes :
  - correction automatique des coordonnées comportant des secondes à 60
- Intégration complète des données Messier (XLSX) dans :
  - les filtres,
  - les tags,
  - les tableaux descriptifs,
  - les cartes stellaires

### Corrigé
- Problèmes d’affichage des labels concentrés au centre des cartes
- Génération incorrecte des PNG astrométriques lorsque seuls les headers WCS sont présents
- Gestion des dossiers exclus :
  - `_sub`
  - `-sub`
- Gestion des permissions Windows lors de la création des dossiers du site
- Régression liée aux métadonnées OpenGraph (fonction manquante)

---

## [00.00.06] – 2025-09-20

### Ajouté
- Cache local pour les requêtes SIMBAD
- Première intégration du catalogue Messier local (XLSX)
- Ajout de l’astrométrie via astrometry.net (optionnelle)

### Modifié
- Amélioration de la détection automatique :
  - type d’objet,
  - catalogue,
  - nom principal
- Génération de pages objet individuelles

### Corrigé
- Exclusion des fichiers `*_thn.jpg`
- Exclusion correcte des dossiers `_sub`

---

## [00.00.05] – 2025-09-10

### Ajouté
- Recherche textuelle dynamique côté client
- Filtres par type d’objet et catalogue
- Génération de sitemap.xml et robots.txt

### Modifié
- Amélioration de la structure HTML5
- Intégration de Bootstrap 5

---

## [00.00.04] – 2025-08-25

### Ajouté
- Génération automatique d’une galerie statique HTML
- Détection automatique des images finales Seestar S50

---

## [00.00.03] – 2025-08-10

### Ajouté
- Extraction des métadonnées FITS
- Structuration initiale des pages

---

## [00.00.02] – 2025-07-30

### Ajouté
- Scan récursif du répertoire MyWorks
- Détection des images JPEG finales

---

## [00.00.01] – 2025-07-15

### Ajouté
- Prototype initial de génération de galerie
- Organisation par répertoires d’objets

---

**Auteur**  
Steve Prud’Homme
