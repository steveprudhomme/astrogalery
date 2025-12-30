# ROADMAP — GNU Astro Galery
**Versioning:** SemVer (MAJOR.MINOR.PATCH) — ex. `0.8.1`, `0.9.0`, `1.0.0`  
**Principe:** La roadmap ci-dessous est basée uniquement sur les fonctionnalités et objectifs explicitement exprimés pour le projet (pas de “feature wishlist” inventée).

---

## Vision (FR / EN)

**FR** — Faire de GNU Astro Galery un générateur de galerie astrophotographique **statique**, **beau**, **documenté**, et **maintenable**, avec des pages objet riches (catalogues + conditions), et une discipline de développement exemplaire.  
**EN** — Make GNU Astro Galery a **static**, **beautiful**, **well‑documented**, and **maintainable** astrophotography gallery generator, with rich object pages (catalogs + observing conditions) and strong development discipline.

---

## Priorités globales

1. **Stabilité et maintenabilité sans changer le comportement** (refactor modulaire, lisibilité, pédagogie).  
2. **Enrichissement des caractéristiques d’objets** depuis des catalogues locaux (Objets divers, puis NGCObjects).  
3. **Bloc “météo spatiale / conditions”** plus complet (Bortle, seeing, nuages, lune).  
4. **Renforcer la robustesse** (règles, tests, CI, qualité).

---

## Plan de versions (proposé et priorisé)

### PATCH (0.8.x) — Qualité interne, pas de changement fonctionnel
> Objectif : réduire la taille de `generate_gallery.py`, clarifier l’architecture, et rendre le code pédagogique **sans modifier le comportement**.

#### v0.8.1 — Découpage en modules (strictement no‑behavior‑change)
- **Refactor modulaire** de `generate_gallery.py` en sous-modules (exemples) :
  - `io_scan.py` (scan MyWorks, inclusion/exclusion)
  - `fits_meta.py` (lecture FITS, extraction headers)
  - `catalog_messier.py` (chargement + lookup)
  - `catalog_divers.py` (chargement + lookup multi-onglets)
  - `simbad_enrich.py` (cache + requêtes)
  - `astrometry_client.py` (Nova/astrometry.net + cache)
  - `starchart.py` (cartes atlas + labels)
  - `site_render.py` (templates HTML, pages, assets, SEO)
  - `cache.py` (stratégies cache, hash, invalidation)
- Maintien strict :
  - mêmes sorties HTML,
  - mêmes noms de fichiers,
  - mêmes règles d’exclusion (`*_sub`, `*-sub`, `*_thn.jpg`),
  - mêmes caches et API calls.

#### v0.8.2 — Commentaires bilingues + style “pédagogique”
- Ajouter des **commentaires FR/EN** sur :
  - les fonctions clés,
  - les structures de données principales,
  - les étapes du pipeline (scan → enrichissement → rendu).
- Ajouter des docstrings courtes : *quoi / pourquoi / entrées / sorties*.

#### v0.8.3 — Discipline de développement + robustesse (NASA “10 rules”)
- Ajouter un document `DEV_RULES.md` :
  - adaptation pragmatique des “NASA 10 rules” au Python (FR/EN).
- Ajouter outillage :
  - `ruff` (lint), `black` (format), `mypy` (types légers) *(si souhaité)*.
- Ajouter scripts :
  - `make lint`, `make format`, `make check` (ou équivalents Windows `.bat` / `.ps1`).

> Remarque versioning : ces changements sont des **PATCH** car ils n’ajoutent pas de nouvelle fonctionnalité utilisateur.

---

### MINOR (0.9.x) — Nouvelles capacités d’enrichissement (compatibles)
> Objectif : enrichir la section **Caractéristiques de l’objet** à partir de catalogues locaux supplémentaires.

#### v0.9.0 — Importer les caractéristiques depuis `objetsdivers.xlsx` (si objet astrophotographié)
- Lorsque l’objet correspond à une entrée du fichier `objetsdivers.xlsx` :
  - importer ses champs (selon les colonnes disponibles),
  - afficher ces valeurs dans **Caractéristiques de l’objet** (page objet),
  - conserver SIMBAD comme source complémentaire si disponible.
- Support multi-onglets : fusionner proprement les entrées.

#### v0.9.1 — Normalisation des champs + affichage cohérent
- Standardiser les clés (FR/EN) pour éviter les variations :
  - ex. “Magnitude”, “Mag”, “Vmag” → `magnitude_v`
- Affichage :
  - ordre stable des champs,
  - unités visibles (mag, al, arcmin…).

---

### MINOR (0.10.x) — NGCObjects (traduction + intégration)
> Objectif : faire pour NGC ce qui existe pour Messier / objets divers.

#### v0.10.0 — Préparer le catalogue NGCObjects (traduction et modèle de données)
- Ajouter un script utilitaire :
  - `tools/ngc_translate.py` ou `tools/ngc_import.py`
- Produire un fichier local exploitable par la galerie :
  - `NGCObjects_fr.xlsx` (ou `NGCObjects_fr.csv`)
- Définir un mapping stable des champs (unités, noms).

#### v0.10.1 — Import NGC dans “Caractéristiques de l’objet”
- Si l’objet est NGC/IC et présent dans NGCObjects_fr :
  - importer les champs,
  - afficher dans **Caractéristiques de l’objet** (page objet),
  - compléter avec SIMBAD si utile.

---

### MINOR (0.11.x) — Météo/conditions d’observation enrichies
> Objectif : compléter la section **Météo spatiale / conditions** sur la page objet.

#### v0.11.0 — Ajouter nuages + température + humidité + pression + vents (si pas déjà) + cache
- Consolider et valider le pipeline basé sur :
  - `DATE-OBS`, `SITELAT`, `SITELONG` (FITS)
  - API météo historique (ex. Open‑Meteo)
- Ajouter **pourcentage de nuages** (cloud cover) si fourni par la source.
- Cache local obligatoire pour éviter les re-requêtes.

#### v0.11.1 — Ajouter phase de la Lune + % illumination
- Calcul local (offline) possible à partir de l’heure UTC + position (astropy/skyfield).
- Afficher :
  - phase (texte),
  - % illumination.

#### v0.11.2 — Ajouter Bortle + seeing (approche stable)
- **Bortle** :
  - option A (offline) : raster/atlas local de pollution lumineuse,
  - option B : valeur “site” configurable si l’utilisateur préfère.
- **Seeing** :
  - si une source fiable est disponible via API, l’utiliser,
  - sinon afficher “N/D” (pas d’invention).

---

### MAJOR (1.0.0) — Stabilisation “release publique”
> Objectif : figer une base stable, documentée, testée, prête à être utilisée et maintenue sur le long terme.

#### v1.0.0 — Critères de sortie (Definition of Done)
- Architecture modulaire finalisée, fichiers courts, responsabilités claires.
- Documentation :
  - README + CHANGELOG + ROADMAP à jour,
  - guide d’installation Windows,
  - guide de contribution (CONTRIBUTING.md).
- Robustesse :
  - tests minimaux (unitaires sur parsers + catalogues),
  - CI GitHub Actions (lint + tests),
  - logs cohérents et niveaux (`INFO/WARN/ERR`).
- Compatibilité :
  - comportement stable,
  - caches stables,
  - pas de “breaking change” non documenté.

---

## Backlog (idées explicitement mentionnées, à planifier après 0.11)
- Améliorer l’ergonomie et la présentation des tableaux de caractéristiques.
- Compléter le bloc météo/conditions avec des champs additionnels si la source est fiable.

---

## Gouvernance des changements (pratique)

- **PATCH** : refactor, commentaires, robustesse, performance, bugfix, doc (sans nouvelle fonctionnalité).  
- **MINOR** : nouvelles fonctions compatibles (nouveaux catalogues, nouveaux champs affichés, nouveaux blocs).  
- **MAJOR** : tout ce qui change la structure de sortie, les conventions de noms, ou requiert une migration.

---

**Auteur / Author**  
Steve Prud’Homme, Laval, Québec.
