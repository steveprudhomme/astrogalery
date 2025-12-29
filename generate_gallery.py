#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import requests
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import ZScaleInterval, ImageNormalize

# Pour fallback JPG (local)
from PIL import Image


# -------------------------
# Configuration
# -------------------------
BOOTSTRAP_CDN_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
BOOTSTRAP_CDN_JS  = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"

ASTRO_NOVA_API  = "https://nova.astrometry.net/api/"
ASTRO_NOVA_SITE = "https://nova.astrometry.net/"

SIMBAD_TAP = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"

ASTROMETRY_MODE = "latest_per_object"
CACHE_PATH = Path("cache") / "object_info.json"

BASE_URL = "https://example.com/seestar"
SITE_TITLE = "Galerie Seestar S50"
CREATOR_NAME = "Steve Prud’Homme"

LOCAL_OBJECT_DB = {
    "M 51": ("galaxie spirale", "spiral galaxy",
             ["galaxie", "galaxie spirale", "interaction"],
             ["galaxy", "spiral galaxy", "interaction"]),
    "M 77": ("galaxie spirale", "spiral galaxy",
             ["galaxie", "galaxie spirale"],
             ["galaxy", "spiral galaxy"]),
    "M 94": ("galaxie spirale", "spiral galaxy",
             ["galaxie", "galaxie spirale"],
             ["galaxy", "spiral galaxy"]),
    "IC 342": ("galaxie spirale", "spiral galaxy",
               ["galaxie", "galaxie spirale"],
               ["galaxy", "spiral galaxy"]),
    "JUPITER": ("planète", "planet", ["planète"], ["planet"]),
    "DENEBOLA": ("étoile", "star", ["étoile"], ["star"]),
}

SIMBAD_OTYPE_MAP = {
    "G":   (["galaxie"], ["galaxy"]),
    "GiG": (["galaxie", "interaction"], ["galaxy", "interaction"]),
    "GPair": (["paire de galaxies"], ["galaxy pair"]),
    "ClG": (["amas de galaxies"], ["galaxy cluster"]),
    "GlC": (["amas globulaire"], ["globular cluster"]),
    "OpC": (["amas ouvert"], ["open cluster"]),
    "PN":  (["nébuleuse planétaire"], ["planetary nebula"]),
    "HII": (["région HII", "nébuleuse"], ["HII region", "nebula"]),
    "SNR": (["reste de supernova"], ["supernova remnant"]),
    "Neb": (["nébuleuse"], ["nebula"]),
    "RfN": (["nébuleuse par réflexion"], ["reflection nebula"]),
    "DNe": (["nébuleuse sombre"], ["dark nebula"]),
    "Star": (["étoile"], ["star"]),
    "Pl": (["planète"], ["planet"]),
    "SyS": (["étoile binaire"], ["binary star"]),
}


# ------------------------------------------------------------
# Utilitaires
# ------------------------------------------------------------
def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text, flags=re.UNICODE)
    return text[:120] if text else "unknown"


def safe_text(x, default=""):
    s = "" if x is None else str(x)
    s = s.strip()
    return s if s else default


def parse_date(date_obs: str):
    s = safe_text(date_obs, "")
    if not s:
        return None
    candidates = [
        ("%Y-%m-%dT%H:%M:%S", s[:19]),
        ("%Y-%m-%d %H:%M:%S", s[:19]),
        ("%Y-%m-%dT%H:%M:%S.%f", s),
        ("%Y-%m-%d %H:%M:%S.%f", s),
        ("%Y-%m-%d", s[:10]),
    ]
    for fmt, val in candidates:
        try:
            return datetime.strptime(val, fmt)
        except Exception:
            pass
    return None


def uniq_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        if not x:
            continue
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def html_escape(s: str) -> str:
    s = s or ""
    return (s.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;")
              .replace('"', "&quot;")
              .replace("'", "&#039;"))


# ------------------------------------------------------------
# Cache SIMBAD
# ------------------------------------------------------------
def load_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache_path: Path, cache: dict):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------
# Catalogue / classification
# ------------------------------------------------------------
def normalize_catalog_id(name: str) -> str | None:
    s = (name or "").strip().upper()
    if s in ("JUPITER", "DENEBOLA"):
        return s

    m = re.search(r"\bM\s*([0-9]{1,3})\b", s)
    if m: return f"M {int(m.group(1))}"

    m = re.search(r"\bNGC\s*([0-9]{1,5})\b", s)
    if m: return f"NGC {int(m.group(1))}"

    m = re.search(r"\bIC\s*([0-9]{1,5})\b", s)
    if m: return f"IC {int(m.group(1))}"

    m = re.search(r"\bSH2[-\s]*([0-9]{1,4})\b", s)
    if m: return f"Sh2-{int(m.group(1))}"

    return None


def infer_catalog(object_name: str):
    up = (object_name or "").strip().upper()
    if re.match(r"^M\s*\d+", up):
        return "Messier"
    if up.startswith("NGC"):
        return "NGC"
    if up.startswith("IC"):
        return "IC"
    if up.startswith("SH2") or "SH2-" in up or "SH 2" in up:
        return "Sharpless"
    return "Other"


def infer_object_type_basic(object_name: str):
    up = (object_name or "").strip().upper()
    if up in ("JUPITER", "SATURN", "MARS", "VENUS"):
        return "Planet"
    if up in ("DENEBOLA",):
        return "Star"
    return "Other"


# ------------------------------------------------------------
# SIMBAD (TAP)
# ------------------------------------------------------------
def _simbad_query_basic(ident: str) -> dict | None:
    adql = f"""
    SELECT TOP 1 b.main_id, b.otype, b.otype_txt
    FROM basic AS b
    JOIN ident AS i ON i.oidref = b.oid
    WHERE i.id = '{ident.replace("'", "''")}'
    """
    r = requests.post(
        SIMBAD_TAP,
        data={"request": "doQuery", "lang": "adql", "format": "json", "query": adql},
        timeout=60
    )
    r.raise_for_status()
    data = r.json()
    rows = data.get("data", [])
    if not rows:
        return None
    fields = [f["name"] for f in data.get("fields", [])]
    row = dict(zip(fields, rows[0]))
    return {
        "main_id": row.get("main_id") or "",
        "otype": row.get("otype") or "",
        "otype_txt": row.get("otype_txt") or "",
    }


def enrich_tags(object_name: str, cache: dict) -> dict:
    ident = normalize_catalog_id(object_name) or object_name.strip()
    ident_key = ident.upper()

    if ident_key in LOCAL_OBJECT_DB:
        t_fr, t_en, tags_fr, tags_en = LOCAL_OBJECT_DB[ident_key]
        return {
            "ident": ident,
            "main_id": ident,
            "otype": "",
            "otype_txt": f"{t_en} / {t_fr}",
            "tags_fr": tags_fr,
            "tags_en": tags_en,
            "source": "local"
        }

    if ident_key in cache:
        return cache[ident_key]

    try:
        info = _simbad_query_basic(ident)
    except Exception as e:
        out = {"ident": ident, "main_id": "", "otype": "", "otype_txt": "", "tags_fr": [], "tags_en": [], "source": f"simbad_error:{e}"}
        cache[ident_key] = out
        return out

    if not info:
        out = {"ident": ident, "main_id": "", "otype": "", "otype_txt": "", "tags_fr": [], "tags_en": [], "source": "simbad_not_found"}
        cache[ident_key] = out
        return out

    otype = info.get("otype", "")
    otype_txt = info.get("otype_txt", "")

    tags_fr, tags_en = SIMBAD_OTYPE_MAP.get(otype, ([], []))
    if not tags_fr and otype_txt:
        tags_fr = [otype_txt.lower()]
    if not tags_en and otype_txt:
        tags_en = [otype_txt.lower()]

    out = {
        "ident": ident,
        "main_id": info.get("main_id", ""),
        "otype": otype,
        "otype_txt": otype_txt,
        "tags_fr": tags_fr,
        "tags_en": tags_en,
        "source": "simbad"
    }
    cache[ident_key] = out
    return out


# ------------------------------------------------------------
# FITS / métadonnées
# ------------------------------------------------------------
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
    # tolère .fit, .fits, .fit.gz, etc
    for p in obs_dir.rglob("Stacked*.fit*"):
        return p
    return None


def estimate_scale_arcsec_per_pix(fits_path: Path):
    try:
        with fits.open(fits_path, ignore_missing_simple=True) as hdul:
            h = hdul[0].header
        focal = h.get("FOCALLEN") or h.get("FOCAL") or h.get("FOCAL_LENGTH") or h.get("TELFOCAL")
        pix_um = h.get("XPIXSZ") or h.get("PIXSIZE") or h.get("PIXELSIZE") or h.get("PIX_SIZE") or h.get("XPIXELSZ")
        if focal is not None and pix_um is not None:
            focal = float(focal)     # mm
            pix_um = float(pix_um)   # microns
            if focal > 0 and pix_um > 0:
                return 206.265 * (pix_um / focal)
    except Exception:
        pass
    return None


# ------------------------------------------------------------
# Lecture image: FITS robuste
# ------------------------------------------------------------
def _to_2d_array(arr: np.ndarray) -> np.ndarray | None:
    """
    Transforme un array FITS en image 2D si possible.
    - Si 2D: ok
    - Si >2D: squeeze puis prend le premier plan/dernières dimensions
    """
    if arr is None:
        return None
    arr = np.array(arr)
    arr = np.squeeze(arr)

    if arr.ndim == 2:
        return arr

    # Ex: (n, y, x) -> prendre arr[0]
    if arr.ndim == 3:
        # Choix simple: premier plan
        return arr[0] if arr.shape[0] <= 20 else arr[-1]

    # Ex: (a,b,y,x) -> prendre [0,0]
    if arr.ndim >= 4:
        # On va sélectionner en cascade les premières dimensions jusqu'à 2D
        while arr.ndim > 2:
            arr = arr[0]
        return arr if arr.ndim == 2 else None

    return None


def read_best_image_from_fits(fits_path: Path) -> np.ndarray | None:
    """
    Essaie de lire une image 2D depuis n'importe quel HDU.
    Gère 2D/3D/4D.
    """
    try:
        with fits.open(fits_path, ignore_missing_simple=True) as hdul:
            # Priorité: HDU ayant de la data
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


# ------------------------------------------------------------
# Fallback image: JPG -> numpy (grayscale)
# ------------------------------------------------------------
def read_image_from_jpg(jpg_path: Path) -> np.ndarray | None:
    try:
        im = Image.open(jpg_path).convert("L")  # grayscale
        return np.array(im)
    except Exception as e:
        print(f"[WARN] Lecture JPG échouée {jpg_path.name}: {e}")
        return None


# ------------------------------------------------------------
# Découverte des JPG finaux
# ------------------------------------------------------------
def is_in_sub_folder(path: Path) -> bool:
    for part in path.parts:
        if part.lower().endswith("_sub"):
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

        if d.name.lower().endswith("_sub"):
            dirnames[:] = []
            continue

        dirnames[:] = [x for x in dirnames if not x.lower().endswith("_sub")]

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
def _json_or_raise(r: requests.Response, context: str) -> dict:
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        raise RuntimeError(
            f"{context}: réponse non-JSON. Content-Type={(r.headers.get('Content-Type') or '')}. Début: {r.text[:200]!r}"
        )


def nova_login(api_key: str) -> str:
    payload = {"apikey": api_key}
    r = requests.post(
        ASTRO_NOVA_API + "login",
        data={"request-json": json.dumps(payload)},
        headers={"Accept": "application/json"},
        timeout=60
    )
    data = _json_or_raise(r, "Login Nova échoué")
    if data.get("status") != "success":
        raise RuntimeError(f"Login Nova échoué: {data}")
    return data["session"]


def nova_upload_fits(session: str, fits_path: Path, scale_arcsec_per_pix=None):
    upload_kwargs = {
        "session": session,
        "allow_commercial_use": "d",
        "allow_modifications": "d",
        "publicly_visible": "n",
    }
    if scale_arcsec_per_pix:
        upload_kwargs.update({
            "scale_units": "arcsecperpix",
            "scale_est": str(scale_arcsec_per_pix),
            "scale_err": "0.25",
        })

    files = {"file": open(fits_path, "rb")}
    try:
        r = requests.post(
            ASTRO_NOVA_API + "upload",
            data={"request-json": json.dumps(upload_kwargs)},
            files=files,
            headers={"Accept": "application/json"},
            timeout=300
        )
        data = _json_or_raise(r, "Upload Nova échoué")
        if data.get("status") != "success":
            raise RuntimeError(f"Upload Nova échoué: {data}")
        return data["subid"]
    finally:
        files["file"].close()


def nova_poll_submission(subid: int, wait_s: int = 5, timeout_s: int = 600):
    t0 = time.time()
    while True:
        r = requests.get(ASTRO_NOVA_API + f"submissions/{subid}", timeout=60)
        data = _json_or_raise(r, f"Submission Nova échouée (subid={subid})")
        jobs = data.get("jobs") or []
        job_ids = [j for j in jobs if isinstance(j, int)]
        if job_ids:
            return job_ids[0]
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"Timeout: aucun job pour subid={subid} après {timeout_s}s")
        time.sleep(wait_s)


def nova_poll_job_solved(jobid: int, wait_s: int = 5, timeout_s: int = 900):
    t0 = time.time()
    while True:
        r = requests.get(ASTRO_NOVA_API + f"jobs/{jobid}", timeout=60)
        data = _json_or_raise(r, f"Job Nova échoué (jobid={jobid})")
        st = data.get("status")
        if st == "success":
            return True
        if st in ("failure", "error"):
            return False
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"Timeout: jobid={jobid} non résolu après {timeout_s}s")
        time.sleep(wait_s)


def looks_like_fits_bytes(b: bytes) -> bool:
    head = b[:80]
    try:
        s = head.decode("ascii", errors="ignore")
    except Exception:
        return False
    return "SIMPLE" in s


def download_binary(url: str, timeout: int = 300) -> tuple[bytes, str]:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.content, (r.headers.get("Content-Type") or "")


def nova_download_wcs_header_only(jobid: int, out_fits_path: Path) -> bool:
    out_fits_path.parent.mkdir(parents=True, exist_ok=True)
    url = ASTRO_NOVA_SITE + f"wcs_file/{jobid}"
    b, ct = download_binary(url, timeout=300)
    if not looks_like_fits_bytes(b):
        snippet = b[:300].decode("utf-8", errors="ignore")
        print(f"\n[WARN] wcs_file non-FITS jobid={jobid} (Content-Type={ct}). Début: {snippet!r}")
        return False
    out_fits_path.write_bytes(b)
    print(f"\n[OK] Téléchargé WCS header-only jobid={jobid} -> {out_fits_path.name} (Content-Type={ct})")
    return True


# ------------------------------------------------------------
# ASTROMÉTRIE PNG (image + WCS header-only)
# ------------------------------------------------------------
def make_astrometry_png_from_image_and_wcs(
    image_array_2d: np.ndarray,
    wcs_header: fits.Header,
    out_png: Path,
    title: str = ""
) -> bool:
    try:
        # Injecter NAXIS si absent (important quand WCS header-only ne le fournit pas)
        h = wcs_header.copy()
        ny, nx = image_array_2d.shape
        if h.get("NAXIS", None) is None:
            h["NAXIS"] = 2
        if h.get("NAXIS1", None) is None:
            h["NAXIS1"] = nx
        if h.get("NAXIS2", None) is None:
            h["NAXIS2"] = ny

        wcs = WCS(h, naxis=2)

        norm = ImageNormalize(image_array_2d, interval=ZScaleInterval())

        fig = plt.figure(figsize=(6, 9), dpi=160)
        ax = fig.add_subplot(111, projection=wcs)

        ax.imshow(image_array_2d, origin="lower", norm=norm)
        ax.grid(color="white", alpha=0.35, linestyle="-", linewidth=0.6)
        ax.set_xlabel("RA")
        ax.set_ylabel("DEC")

        if title:
            ax.set_title(title, fontsize=11)

        cx, cy = nx / 2, ny / 2
        radius_pix = min(nx, ny) * 0.33
        ax.add_patch(plt.Circle((cx, cy), radius_pix, fill=False, lw=1.2, alpha=0.85))

        out_png.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(out_png)
        plt.close(fig)

        print(f"[OK] PNG écrit (image+WCS): {out_png}")
        return True
    except Exception as e:
        print(f"\n[WARN] PNG astrométrie impossible: {e}")
        return False


def load_wcs_header_only(wcs_fits_path: Path) -> fits.Header | None:
    try:
        with fits.open(wcs_fits_path, ignore_missing_simple=True) as hdul:
            return hdul[0].header
    except Exception as e:
        print(f"[WARN] Lecture WCS header-only échouée {wcs_fits_path.name}: {e}")
        return None


# ------------------------------------------------------------
# SEO meta + JSON-LD
# ------------------------------------------------------------
def og_meta(title: str, description: str, image_url_abs: str, url_abs: str) -> str:
    return f"""
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html_escape(title)}">
  <meta property="og:description" content="{html_escape(description)}">
  <meta property="og:image" content="{html_escape(image_url_abs)}">
  <meta property="og:url" content="{html_escape(url_abs)}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html_escape(title)}">
  <meta name="twitter:description" content="{html_escape(description)}">
  <meta name="twitter:image" content="{html_escape(image_url_abs)}">
"""


def image_jsonld(item: dict, page_url: str) -> dict:
    add_props = []
    for k in ["ra", "dec", "exptime", "filter", "telescope", "instrument"]:
        v = item.get(k)
        if v not in (None, "", 0, "0"):
            add_props.append({"@type": "PropertyValue", "name": k.upper(), "value": str(v)})

    keywords = uniq_preserve(
        (item.get("keywords_fr", []) + item.get("keywords_en", []) + item.get("tags_fr", []) + item.get("tags_en", []))
    )

    return {
        "@context": "https://schema.org",
        "@type": "ImageObject",
        "name": item.get("objectName") or item.get("name"),
        "description": item.get("description", ""),
        "keywords": ", ".join(keywords),
        "contentUrl": item["contentUrlAbs"],
        "thumbnailUrl": item["thumbnailUrlAbs"],
        "dateCreated": item.get("dateCreatedISO", "") or item.get("dateCreated", ""),
        "about": {"@type": "Thing", "name": item.get("objectName", "")},
        "isPartOf": {"@type": "CollectionPage", "name": SITE_TITLE, "url": BASE_URL.rstrip("/") + "/index.html"},
        "creator": {"@type": "Person", "name": CREATOR_NAME},
        "url": page_url,
        "additionalProperty": add_props
    }


# ------------------------------------------------------------
# HTML builders
# ------------------------------------------------------------
def build_index_html(title: str, og_block: str) -> str:
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(title)}</title>
  <meta name="description" content="Galerie astrophotographie — Seestar S50">
{og_block}
  <link rel="stylesheet" href="{BOOTSTRAP_CDN_CSS}">
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body class="bg-body-tertiary">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand" href="index.html">{html_escape(title)}</a>
  </div>
</nav>

<main class="container py-4">
  <div class="row g-3 align-items-end">
    <div class="col-md-6">
      <label class="form-label">Recherche</label>
      <input id="searchInput" class="form-control" placeholder="M31, NGC7000, nebula, galaxy...">
    </div>
    <div class="col-md-3">
      <label class="form-label">Type</label>
      <select id="typeSelect" class="form-select">
        <option value="">Tous / All</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label">Catalogue</label>
      <select id="catalogSelect" class="form-select">
        <option value="">Tous / All</option>
      </select>
    </div>
  </div>

  <hr class="my-4">
  <div id="stats" class="text-muted small mb-3"></div>
  <div id="grid" class="row g-3"></div>
</main>

<script id="images-data" type="application/json"></script>

<script src="{BOOTSTRAP_CDN_JS}"></script>
<script src="assets/js/app.js"></script>
</body>
</html>
"""


def build_object_page_html(site_title: str, obj_name: str, jsonld_block: str, og_block: str, items: list) -> str:
    astro = items[0].get("astrometryUrl", "")
    astro_block = ""
    if astro:
        astro_block = f"""
  <div class="mb-4">
    <div class="card shadow-sm">
      <div class="card-body">
        <div class="fw-semibold mb-2">Astrométrie / Astrometry</div>
        <img src="../{html_escape(astro)}" class="img-fluid rounded" alt="Astrométrie {html_escape(obj_name)}">
      </div>
    </div>
  </div>
"""

    cards = []
    for it in items:
        tags_line = ", ".join(uniq_preserve(it.get("tags_fr", []) + it.get("tags_en", []))[:6])
        astro_link = ""
        if it.get("astrometryUrl"):
            astro_link = f"""<div class="mt-2 small"><a href="../{html_escape(it['astrometryUrl'])}" target="_blank" rel="noopener">Astrométrie</a></div>"""

        cards.append(f"""
        <div class="col-md-4">
          <div class="card h-100 shadow-sm">
            <a href="../{html_escape(it['contentUrl'])}" target="_blank" rel="noopener">
              <img src="../{html_escape(it['thumbnailUrl'])}" class="card-img-top" alt="{html_escape(it['alt'])}">
            </a>
            <div class="card-body">
              <div class="fw-semibold">{html_escape(it.get('objectName', it['name']))}</div>
              <div class="text-muted small">{html_escape(it.get('dateCreated',''))}</div>
              <div class="small mt-2">
                <span class="badge text-bg-secondary">{html_escape(it.get('objectType',''))}</span>
                <span class="badge text-bg-secondary">{html_escape(it.get('catalog',''))}</span>
                <span class="badge text-bg-secondary">{html_escape(str(it.get('filter','')))}</span>
              </div>
              <div class="small text-muted mt-2">{html_escape(tags_line)}</div>
              {astro_link}
            </div>
          </div>
        </div>
        """)
    cards_html = "\n".join(cards)

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(obj_name)} — {html_escape(site_title)}</title>
  <meta name="description" content="Astrophotographie : {html_escape(obj_name)}">
{og_block}
  <link rel="stylesheet" href="{BOOTSTRAP_CDN_CSS}">
  <link rel="stylesheet" href="../assets/css/styles.css">
  <script type="application/ld+json">
{jsonld_block}
  </script>
</head>
<body class="bg-body-tertiary">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand" href="../index.html">{html_escape(site_title)}</a>
    <span class="navbar-text text-white-50 ms-3">{html_escape(obj_name)}</span>
  </div>
</nav>

<main class="container py-4">
  <h1 class="h3 mb-3">{html_escape(obj_name)}</h1>
{astro_block}
  <div class="row g-3">
    {cards_html}
  </div>
</main>

<script src="{BOOTSTRAP_CDN_JS}"></script>
</body>
</html>
"""


def build_app_js() -> str:
    return r"""
function uniq(arr) { return [...new Set(arr)].sort(); }

function fillSelect(select, values) {
  for (const v of values) {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  }
}

function matches(item, q) {
  if (!q) return true;
  const parts = [
    item.name, item.description, item.objectName, item.catalog, item.objectType,
    item.filter,
    ...(item.tags_fr || []), ...(item.tags_en || []),
    ...(item.keywords_fr || []), ...(item.keywords_en || []),
  ];
  const hay = parts.join(' ').toLowerCase();
  return hay.includes(q.toLowerCase());
}

function buildCard(item) {
  const col = document.createElement('div');
  col.className = 'col-12 col-sm-6 col-lg-4';

  const objLink = item.objectPage ? `<div class="mt-2 small"><a href="${item.objectPage}">Page objet</a></div>` : ``;
  const astroLink = item.astrometryUrl ? `<div class="mt-2 small"><a href="${item.astrometryUrl}" target="_blank" rel="noopener">Astrométrie</a></div>` : ``;

  const tags = [...new Set([...(item.tags_fr||[]), ...(item.tags_en||[])])].slice(0,6).join(', ');

  col.innerHTML = `
    <div class="card h-100 shadow-sm">
      <a href="${item.contentUrl}" target="_blank" rel="noopener">
        <img src="${item.thumbnailUrl}" class="card-img-top" alt="${item.alt}">
      </a>
      <div class="card-body">
        <div class="fw-semibold">${item.objectName || item.name}</div>
        <div class="text-muted small">${item.dateCreated || ''}</div>
        <div class="small mt-2">
          <span class="badge text-bg-secondary">${item.objectType || ''}</span>
          <span class="badge text-bg-secondary">${item.catalog || ''}</span>
          <span class="badge text-bg-secondary">${item.filter || ''}</span>
        </div>
        <div class="small text-muted mt-2">${tags}</div>
        ${objLink}
        ${astroLink}
      </div>
    </div>
  `;
  return col;
}

function render(data) {
  const grid = document.getElementById('grid');
  const stats = document.getElementById('stats');
  const q = document.getElementById('searchInput').value.trim();
  const type = document.getElementById('typeSelect').value;
  const catalog = document.getElementById('catalogSelect').value;

  const filtered = data.filter(it => {
    if (type && it.objectType !== type) return false;
    if (catalog && it.catalog !== catalog) return false;
    return matches(it, q);
  });

  grid.innerHTML = '';
  for (const item of filtered) grid.appendChild(buildCard(item));
  stats.textContent = `${filtered.length} image(s) affichée(s) / ${data.length} au total`;
}

(async function main() {
  let data;
  try {
    data = JSON.parse(document.getElementById('images-data').textContent);
  } catch (e) {
    console.error("Erreur chargement données:", e);
    document.getElementById('stats').textContent = "Impossible de charger les données (voir console F12).";
    return;
  }

  data.sort((a, b) => (b.dateCreatedISO || "").localeCompare(a.dateCreatedISO || ""));

  const typeSelect = document.getElementById('typeSelect');
  const catalogSelect = document.getElementById('catalogSelect');
  fillSelect(typeSelect, uniq(data.map(d => d.objectType).filter(Boolean)));
  fillSelect(catalogSelect, uniq(data.map(d => d.catalog).filter(Boolean)));

  document.getElementById('searchInput').addEventListener('input', () => render(data));
  typeSelect.addEventListener('change', () => render(data));
  catalogSelect.addEventListener('change', () => render(data));

  render(data);
})();
"""


def build_styles_css() -> str:
    return """
.card-img-top { object-fit: cover; height: 240px; }
"""


# ------------------------------------------------------------
# Sitemap
# ------------------------------------------------------------
def write_sitemap(site_dir: Path, urls: list[str], base_url: str):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for u in urls:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = base_url.rstrip("/") + "/" + u.lstrip("/")
    tree = ET.ElementTree(urlset)
    tree.write(site_dir / "sitemap.xml", encoding="utf-8", xml_declaration=True)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    root = Path(os.getcwd())
    out = root / "site"

    # IMPORTANT: clé dans variable d'environnement
    NOVA_API_KEY = os.environ.get("NOVA_ASTROMETRY_API_KEY", "").strip()
    if not NOVA_API_KEY:
        print("[INFO] NOVA_ASTROMETRY_API_KEY non défini -> pas d'astrométrie (plate solve)")

    cache = load_cache(root / CACHE_PATH)

    # Rebuild propre
    if out.exists():
        shutil.rmtree(out)
    (out / "assets/css").mkdir(parents=True, exist_ok=True)
    (out / "assets/js").mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(parents=True, exist_ok=True)
    (out / "gallery").mkdir(parents=True, exist_ok=True)
    (out / "data/img").mkdir(parents=True, exist_ok=True)
    (out / "astrometry").mkdir(parents=True, exist_ok=True)
    (out / "data/solved").mkdir(parents=True, exist_ok=True)

    jpgs = find_final_jpgs(root)
    if not jpgs:
        print("Aucun JPG final trouvé (hors dossiers *_sub et hors fichiers *_thn.jpg).")
        return

    total = len(jpgs)
    processed = 0
    print(f"🔎 {total} image(s) à traiter (hors *_sub et hors *_thn.jpg)...")

    items = []
    object_groups = {}

    nova_session = None
    if NOVA_API_KEY:
        try:
            nova_session = nova_login(NOVA_API_KEY)
            print("[INFO] Nova: session OK")
        except Exception as e:
            print(f"[WARN] Login Nova impossible: {e}")
            nova_session = None

    # Pass 1: items + tags
    for jpg_path in jpgs:
        processed += 1
        pct = (processed / total) * 100.0
        print(f"🛠️  Scan+tags: {processed}/{total} ({pct:5.1f}%)", end="\r")

        obs_dir = jpg_path.parent
        fits_path = find_stacked_fits_in_dir(obs_dir)
        meta = extract_fits_metadata(fits_path) if fits_path else {}

        object_name = meta.get("object") or obs_dir.name
        if object_name.strip().lower() in ("unknown object", "unknown", ""):
            object_name = obs_dir.name

        dt = parse_date(meta.get("date_obs", ""))
        date_created_human = dt.strftime("%Y-%m-%d %H:%M") if dt else ""
        date_created_iso = dt.isoformat() if dt else ""

        catalog = infer_catalog(object_name)
        obj_type = infer_object_type_basic(object_name)

        # Copie image finale
        rel_img_name = f"{slugify(object_name)}-{jpg_path.name}"
        rel_img = Path("data/img") / rel_img_name
        shutil.copy2(jpg_path, out / rel_img)

        # Thumbnail (si présent) : copie; sinon fallback vers image
        thn_guess = jpg_path.with_name(jpg_path.stem + "_thn.jpg")
        rel_thn = rel_img
        if thn_guess.exists() and (not is_in_sub_folder(thn_guess)):
            rel_thn_name = f"{slugify(object_name)}-{thn_guess.name}"
            rel_thn = Path("data/img") / rel_thn_name
            shutil.copy2(thn_guess, out / rel_thn)

        enrich = enrich_tags(object_name, cache)
        tags_fr = uniq_preserve(enrich.get("tags_fr", []))
        tags_en = uniq_preserve(enrich.get("tags_en", []))

        # Object type déduit des tags SIMBAD
        if "planetary nebula" in tags_en:
            obj_type = "Planetary Nebula"
        elif "globular cluster" in tags_en:
            obj_type = "Globular Cluster"
        elif "open cluster" in tags_en:
            obj_type = "Open Cluster"
        elif "nebula" in tags_en or "HII region" in tags_en:
            obj_type = "Nebula"
        elif "spiral galaxy" in tags_en:
            obj_type = "Spiral Galaxy"
        elif "galaxy" in tags_en:
            obj_type = "Galaxy"
        elif "star" in tags_en:
            obj_type = "Star"
        elif "planet" in tags_en:
            obj_type = "Planet"

        keywords_fr = uniq_preserve([object_name, catalog, "Seestar S50", "astrophotographie"] + tags_fr)
        keywords_en = uniq_preserve([object_name, catalog, "Seestar S50", "astrophotography"] + tags_en)

        tags_short_fr = ", ".join(tags_fr[:3]) if tags_fr else ""
        tags_short_en = ", ".join(tags_en[:3]) if tags_en else ""
        desc = f"Astrophotographie {object_name} (Seestar S50). {tags_short_fr} / {tags_short_en}".strip()

        alt = f"{object_name} — {', '.join(uniq_preserve(tags_fr[:2] + tags_en[:2]))} — {catalog} — Seestar S50".strip(" —")

        obj_slug = slugify(object_name)
        object_page = f"gallery/{obj_slug}.html"

        content_abs = BASE_URL.rstrip("/") + "/" + rel_img.as_posix()
        thumb_abs = BASE_URL.rstrip("/") + "/" + rel_thn.as_posix()

        item = {
            "name": jpg_path.name,
            "objectName": object_name,
            "catalog": catalog,
            "objectType": obj_type,
            "dateCreated": date_created_human,
            "dateCreatedISO": date_created_iso,
            "filter": meta.get("filter", ""),
            "exptime": meta.get("exptime", ""),
            "telescope": meta.get("telescope", ""),
            "instrument": meta.get("instrument", ""),
            "ra": meta.get("ra", ""),
            "dec": meta.get("dec", ""),

            "tags_fr": tags_fr,
            "tags_en": tags_en,
            "keywords_fr": keywords_fr,
            "keywords_en": keywords_en,

            "description": desc,
            "alt": alt,

            "contentUrl": rel_img.as_posix(),
            "thumbnailUrl": rel_thn.as_posix(),
            "contentUrlAbs": content_abs,
            "thumbnailUrlAbs": thumb_abs,

            "objectPage": object_page,
            "astrometryUrl": "",

            "_fitsPath": str(fits_path) if fits_path else "",
            "_jpgPath": str(jpg_path),
            "_jpgStem": jpg_path.stem,
        }

        items.append(item)
        object_groups.setdefault(object_name, []).append(item)

    save_cache(root / CACHE_PATH, cache)
    print("\n✅ Tags: terminé (cache mis à jour).")

    # Tri global récent -> ancien
    items.sort(key=lambda x: x.get("dateCreatedISO", ""), reverse=True)

    # Pass 2: astrométrie
    if nova_session:
        if ASTROMETRY_MODE == "all":
            to_solve = [it for it in items if it.get("_fitsPath")]
        else:
            to_solve = []
            for obj, group in object_groups.items():
                group.sort(key=lambda x: x.get("dateCreatedISO", ""), reverse=True)
                if group and group[0].get("_fitsPath"):
                    to_solve.append(group[0])

        print(f"[INFO] Astrométrie mode={ASTROMETRY_MODE} -> {len(to_solve)} solve(s)")

        done = 0
        for it in to_solve:
            done += 1
            obj = it["objectName"]
            fits_path = Path(it["_fitsPath"]) if it.get("_fitsPath") else None
            jpg_path = Path(it["_jpgPath"])
            jpg_stem = it["_jpgStem"]
            pct = (done / max(1, len(to_solve))) * 100.0
            print(f"🌐 Astrométrie: {done}/{len(to_solve)} ({pct:5.1f}%) — {obj}", end="\r")

            try:
                if not fits_path or not fits_path.exists():
                    print(f"\n[WARN] Pas de FITS local pour {obj} -> astrométrie skip")
                    continue

                wcs_fits = out / "data/solved" / f"{slugify(obj)}-{jpg_stem}-wcs.fits"

                if not wcs_fits.exists():
                    scale = estimate_scale_arcsec_per_pix(fits_path)
                    subid = nova_upload_fits(nova_session, fits_path, scale_arcsec_per_pix=scale)
                    jobid = nova_poll_submission(subid, wait_s=5, timeout_s=600)
                    ok = nova_poll_job_solved(jobid, wait_s=5, timeout_s=900)
                    if not ok:
                        print(f"\n[WARN] Plate-solve échoué (job failure) pour {obj}")
                        continue

                    ok_dl = nova_download_wcs_header_only(jobid, wcs_fits)
                    if not ok_dl:
                        print(f"\n[WARN] Téléchargement WCS header-only échoué pour {obj}")
                        continue

                wcs_header = load_wcs_header_only(wcs_fits)
                if wcs_header is None:
                    continue

                # 1) Essayer image depuis FITS (robuste)
                img = read_best_image_from_fits(fits_path)

                # 2) Fallback : utiliser le JPG final si FITS ne donne pas d'image 2D
                if img is None:
                    print(f"\n[WARN] Image FITS invalide: aucun HDU 2D dans {fits_path.name} -> fallback JPG")
                    img = read_image_from_jpg(jpg_path)

                if img is None:
                    print(f"\n[WARN] Aucun pixel image disponible (FITS+JPG) pour {obj}")
                    continue

                astro_name = f"{slugify(obj)}-{jpg_stem}-astrometry.png"
                astro_rel = Path("astrometry") / astro_name

                ok_png = make_astrometry_png_from_image_and_wcs(
                    image_array_2d=img,
                    wcs_header=wcs_header,
                    out_png=out / astro_rel,
                    title=obj
                )

                if ok_png:
                    it["astrometryUrl"] = astro_rel.as_posix()
                    print(f"\n[OK] Lien astrométrie: {it['astrometryUrl']}")
                else:
                    print(f"\n[WARN] PNG astrométrie non généré: {obj}")

            except Exception as e:
                print(f"\n[WARN] Astrométrie échouée pour {obj}: {e}")

        print("\n✅ Astrométrie: terminé.")
    else:
        print("[INFO] Astrométrie non exécutée (pas de session Nova).")

    # Nettoyage champs internes
    for it in items:
        it.pop("_fitsPath", None)
        it.pop("_jpgPath", None)
        it.pop("_jpgStem", None)

    print("🧩 Écriture des fichiers du site...")

    (out / "data/images.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    og_img = items[0]["thumbnailUrlAbs"] if items else (BASE_URL.rstrip("/") + "/")
    og_index = og_meta(SITE_TITLE, "Galerie astrophotographie — Seestar S50", og_img, BASE_URL.rstrip("/") + "/index.html")

    index_html = build_index_html(SITE_TITLE, og_index)
    index_html = index_html.replace(
        '<script id="images-data" type="application/json"></script>',
        '<script id="images-data" type="application/json">\n' +
        json.dumps(items, ensure_ascii=False) +
        '\n</script>'
    )
    (out / "index.html").write_text(index_html, encoding="utf-8")

    (out / "assets/js/app.js").write_text(build_app_js(), encoding="utf-8")
    (out / "assets/css/styles.css").write_text(build_styles_css(), encoding="utf-8")

    # Pages objets
    object_urls = []
    for obj_name, group_items in object_groups.items():
        group_items.sort(key=lambda x: x.get("dateCreatedISO", ""), reverse=True)

        top = group_items[0]
        page_rel = f"gallery/{slugify(obj_name)}.html"
        page_url_abs = BASE_URL.rstrip("/") + "/" + page_rel

        og_obj = og_meta(
            f"{obj_name} — {SITE_TITLE}",
            top.get("description", f"Astrophotographie: {obj_name}"),
            top["thumbnailUrlAbs"],
            page_url_abs
        )

        jsonld = image_jsonld(top, page_url_abs)

        page = build_object_page_html(
            SITE_TITLE,
            obj_name,
            json.dumps(jsonld, ensure_ascii=False, indent=2),
            og_obj,
            group_items
        )

        page_path = out / "gallery" / f"{slugify(obj_name)}.html"
        page_path.write_text(page, encoding="utf-8")
        object_urls.append(page_rel)

    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: sitemap.xml\n",
        encoding="utf-8"
    )

    write_sitemap(out, ["index.html"] + object_urls, BASE_URL)

    print(f"✅ Galerie générée dans: {out}")
    print(f"📌 Cache SIMBAD: {root / CACHE_PATH}")
    if BASE_URL.startswith("https://example.com"):
        print("⚠️  Mets BASE_URL sur ton URL réelle si tu publies (sinon OG/sitemap ont une URL fictive).")


if __name__ == "__main__":
    main()
