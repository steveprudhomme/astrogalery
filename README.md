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

## Table des matières

- Fonctionnalités
- Philosophie du projet
- Structure des données
- Prérequis
- Installation
- Utilisation
- Catalogue Messier (XLSX)
- Catalogue d’objets divers (XLSX)
- Enrichissement astronomique (SIMBAD)
- Pages objet
- Astrométrie
- Cartes stellaires (atlas)
- Cache
- Météo spatiale et conditions d’observation
- Règles d’inclusion / exclusion
- SEO et métadonnées
- Dépannage
- Sécurité et bonnes pratiques
- Publication
- Licence
- Crédits

---

## Fonctionnalités

- Génération complète d’un **site Web statique**
- Page d’accueil :
  - toutes les images détectées
  - tri chronologique (plus récent → plus ancien)
  - recherche textuelle instantanée
  - filtres dynamiques (types, catalogues)
- Navigation naturelle :
  - clic sur l’image → page objet
- Pages objet comprenant :
  - image principale mise en valeur
  - auteur et licence
  - métadonnées FITS complètes
  - caractéristiques astronomiques
  - image astrométrique cliquable
  - **carte stellaire de type atlas**
  - bloc de **conditions d’observation / météo spatiale**
- Enrichissement automatique via :
  - SIMBAD
  - catalogue Messier local (XLSX)
  - catalogue d’objets divers multi-feuilles (XLSX)
- Astrométrie automatique (optionnelle)
- Mise en cache intelligente (requêtes, images, cartes)
- SEO intégré :
  - sitemap.xml
  - robots.txt
  - OpenGraph
  - JSON-LD (schema.org / ImageObject)

---

## Philosophie du projet

GNU Astro Galery repose sur quelques principes clés :

- **Une image correspond à un objet astronomique**
- **Chaque objet possède sa propre page documentaire**
- Les données doivent être :
  - traçables,
  - reproductibles,
  - basées sur des sources ouvertes
- Le site généré doit rester lisible dans 10 ans sans dépendance serveur

---

## Structure des données

Le script analyse un répertoire racine contenant :

- images finales (JPEG / PNG / FITS convertis)
- fichiers FITS associés
- sous-répertoires d’objets

Les noms de répertoires sont utilisés comme **clé primaire astronomique**
(Messier, NGC, IC, nom usuel).

---

## Prérequis

- Python **3.10+**
- Librairies principales :
  - astropy
  - astroquery
  - numpy
  - pandas
  - matplotlib
  - pillow
  - requests
  - openpyxl
- Compte astrometry.net (optionnel)

---

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

---

## Utilisation

```bash
python generate_gallery.py
```

Le site est généré dans le dossier :

```text
site/
```

---

## Catalogue Messier (XLSX)

- Fichier local : `Objets Messiers.xlsx`
- Utilisé pour :
  - type d’objet
  - magnitude
  - taille apparente
  - distance
  - constellation
- Les données Messier sont **prioritaires** sur SIMBAD.

---

## Catalogue d’objets divers (XLSX)

- Fichier multi-feuilles : `objetsdivers.xlsx`
- Inclusion conditionnelle :
  - objets de magnitude **≤ 6**
- Utilisé pour enrichir les **cartes stellaires** uniquement.

---

## Enrichissement astronomique (SIMBAD)

SIMBAD est utilisé pour :
- coordonnées précises
- désignations alternatives
- types astrophysiques

Toutes les requêtes sont mises en cache localement.

---

## Pages objet

Chaque page objet inclut :

1. Image principale
2. Auteur : **Steve Prud’Homme**
3. Licence : **Creative Commons CC0 1.0**
4. Métadonnées FITS (tableau)
5. Caractéristiques astronomiques (tableau)
6. Image astrométrique
7. Carte stellaire (atlas)
8. Bloc conditions d’observation / météo spatiale

---

## Astrométrie

- Basée sur **astrometry.net**
- Support des FITS avec ou sans image 2D
- Génération PNG annotée
- Mise en cache automatique

---

## Cartes stellaires (atlas)

- Générées localement (matplotlib + astropy)
- Projection plane centrée sur l’objet
- Éléments affichés :
  - objets Messier
  - objets divers (mag ≤ 6)
- Noms positionnés sous leur symbole

---

## Cache

Sont mis en cache :
- requêtes SIMBAD
- résultats d’astrométrie
- cartes stellaires

Objectif : éviter toute requête inutile lors des régénérations.

---

## Météo spatiale et conditions d’observation

À partir des en-têtes FITS (`DATE-OBS`, `SITELAT`, `SITELONG`) :

- seeing (estimé)
- échelle de Bortle (approximée)
- température
- humidité
- pression atmosphérique
- vent (direction et vitesse)

Les données sont récupérées via des APIs météo open source.

---

## Règles d’inclusion / exclusion

Sont exclus automatiquement :
- répertoires `_sub` et `-sub`
- fichiers miniatures `*_thn.jpg`

---

## SEO et métadonnées

- OpenGraph par page
- JSON-LD ImageObject
- sitemap.xml automatique
- robots.txt

---

## Dépannage

- Vérifier les messages `[WARN]` dans la console
- Supprimer le cache en cas de changement majeur
- Tester sur un sous-ensemble réduit d’images

---

## Sécurité et bonnes pratiques

- Site 100 % statique
- Aucune donnée personnelle stockée
- Astrometry.net utilisé uniquement pour la résolution d’images

---

## Publication

Compatible avec :
- GitHub Pages
- Apache / Nginx
- NAS personnels

---

## Licence

- Code : **GNU GPL v3**
- Images : **Creative Commons CC0 1.0** (sauf mention contraire)

---

## Crédits

Conception, développement et astrophotographie :

**Steve Prud’Homme**
