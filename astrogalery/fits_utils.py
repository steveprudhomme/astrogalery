"""Couche FITS (lecture + extraction) — à migrer depuis generate_gallery.py.

Responsabilités:
- Trouver Stacked*.fit(s) associé
- Lire header FITS (ignore_missing_simple=True)
- Extraire DATE-OBS/SITELAT/SITELONG etc.
- Conserver _fitsPath/_jpgPath jusqu'au rendu (important pour météo)

v0.8.1:
- Module prêt; migration à faire par copier-coller sans changer la logique.
"""
