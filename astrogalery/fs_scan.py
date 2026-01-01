"""Couche disque (scan) — extrait de generate_gallery.py (v0.8.1).

FR: Fonctions de découverte des JPG en respectant les exclusions Seestar.
EN: JPG discovery helpers respecting Seestar exclusions.

NOTE no-behavior-change:
- Code copié tel quel depuis generate_gallery.py (sans modification de logique).
"""

import os
from pathlib import Path

def is_in_sub_folder(path: Path) -> bool:
    for part in path.parts:
        p = str(part).lower()
        if p.endswith("_sub") or p.endswith("-sub"):
            return True
    return False


def is_thumbnail_file(path: Path) -> bool:
    return path.name.lower().endswith("_thn.jpg")


def find_final_jpgs(root_dir: Path):
    results = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        d = Path(dirpath)

        if d.name in ("site", ".git", "__pycache__", ".venv", "venv", "cache"):
            dirnames[:] = []
            continue

        if d.name.lower().endswith("_sub") or d.name.lower().endswith("-sub"):
            dirnames[:] = []
            continue

        dirnames[:] = [x for x in dirnames if not (x.lower().endswith("_sub") or x.lower().endswith("-sub"))]

        for fn in filenames:
            if not fn.lower().endswith(".jpg"):
                continue
            p = d / fn
            if is_in_sub_folder(p):
                continue
            if is_thumbnail_file(p):
                continue
            results.append(p)

    return results


# ------------------------------------------------------------
# Nova helpers
# ------------------------------------------------------------

