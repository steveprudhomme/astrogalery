"""FITS utilities (v0.8.1).

FR:
- Fonctions extraites de generate_gallery.py (no-behavior-change).
- Lecture FITS, extraction métadonnées, sélection de l'image, WCS header-only helpers.

EN:
- Functions extracted from generate_gallery.py (no behavior change).
- FITS reading, metadata extraction, best image selection, WCS header-only helpers.

Note:
- This module intentionally keeps the same logic and defaults as the original script.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# --- helper from legacy generate_gallery.py (no-behavior-change) ---
def safe_text(x, default=""):
    s = "" if x is None else str(x)
    s = s.strip()
    return s if s else default
# --- end helper ---


# Third-party
try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

try:
    from astropy.io import fits
    from astropy.wcs import WCS
except Exception:  # pragma: no cover
    fits = None  # type: ignore
    WCS = None  # type: ignore


def extract_fits_metadata(fits_path: Path) -> dict:
    try:
        with fits.open(fits_path, ignore_missing_simple=True) as hdul:
            h = hdul[0].header
            return {
                "object": safe_text(h.get("OBJECT"), "Unknown Object"),
                "date_obs": safe_text(h.get("DATE-OBS"), ""),
                "exptime": h.get("EXPTIME", 0),
                "filter": safe_text(h.get("FILTER"), "None"),
                "telescope": safe_text(h.get("TELESCOP"), "Unknown Telescope"),
                "instrument": safe_text(h.get("INSTRUME"), "Unknown Instrument"),
                "observer": safe_text(h.get("OBSERVER"), "Unknown Observer"),
                "ra": safe_text(h.get("RA"), ""),
                "dec": safe_text(h.get("DEC"), ""),
            }
    except Exception as e:
        print(f"[WARN] FITS illisible: {fits_path} ({e})")
        return {}

def find_stacked_fits_in_dir(obs_dir: Path) -> Path | None:
    for p in obs_dir.rglob("Stacked*.fit*"):
        return p
    return None

def read_best_image_from_fits(fits_path: Path) -> np.ndarray | None:
    try:
        with fits.open(fits_path, ignore_missing_simple=True) as hdul:
            for hdu in hdul:
                data = getattr(hdu, "data", None)
                if data is None:
                    continue
                img = _to_2d_array(data)
                if img is not None and img.size > 0:
                    return img
    except Exception as e:
        print(f"[WARN] Lecture FITS échouée {fits_path.name}: {e}")
        return None
    return None

def wcs_center_from_header(h: fits.Header) -> tuple[float | None, float | None]:
    try:
        ra = h.get("CRVAL1", None)
        dec = h.get("CRVAL2", None)
        ra = float(ra) if ra is not None else None
        dec = float(dec) if dec is not None else None
        return ra, dec
    except Exception:
        return None, None

def load_wcs_header_only(wcs_fits_path: Path) -> fits.Header | None:
    try:
        with fits.open(wcs_fits_path, ignore_missing_simple=True) as hdul:
            return hdul[0].header
    except Exception as e:
        print(f"[WARN] Lecture WCS header-only échouée {wcs_fits_path.name}: {e}")
        return None


# ------------------------------------------------------------
# ASTROMETRY PNG (image + WCS header-only)
# ------------------------------------------------------------

def looks_like_fits_bytes(b: bytes) -> bool:
    head = b[:80]
    try:
        s = head.decode("ascii", errors="ignore")
    except Exception:
        return False
    return "SIMPLE" in s
