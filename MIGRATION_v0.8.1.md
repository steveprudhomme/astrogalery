# v0.8.1 — Découpage en modules (Option A / par couches)

Objectif: découper generate_gallery.py sans changer le comportement.

Ordre recommandé (commits):
1) logging_utils + config (zéro risque)
2) fs_scan (scan disque + exclusions _sub/-sub et _thn)
3) fits_utils (lecture FITS + extraction + chemins internes)
4) catalogs (Messier + objetsdivers)
5) enrich (simbad + tagging)
6) astrometry + charts
7) site (templates + render + SEO)

Conseil: après chaque étape, exécuter et valider que le dossier `site/` généré est identique.
