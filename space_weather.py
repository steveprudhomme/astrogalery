# space_weather.py
# Module pour GNU Astro Galery
#
# Rôle:
# - Extraire (DATE-OBS, SITELAT, SITELONG) depuis un FITS
# - Interroger Open-Meteo (archive API) pour obtenir des conditions météo
# - Retourner un bloc HTML Bootstrap prêt à injecter dans la page objet
#
# Notes:
# - Ce module n'est PAS un script à exécuter directement.
# - Il est importé et utilisé par generate_gallery.py.
#
# Champs FITS attendus:
# - DATE-OBS (ISO 8601, idéalement UTC, ex: 2025-09-19T23:29:26Z)
# - SITELAT, SITELONG (degrés décimaux)
#
# Données météo (UTC):
# - Température (°C)
# - Humidité (%)
# - Pression (hPa)
# - Vent (km/h + direction °)
#
# Cache:
# - Un cache local léger évite de re-télécharger la même heure/site.
#   Fichier: .cache/space_weather_cache.json (à côté du script principal)

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from astropy.io import fits

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"


def _cache_path() -> Path:
    return Path(".cache") / "space_weather_cache.json"


def _load_cache() -> Dict[str, Any]:
    p = _cache_path()
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    p = _cache_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Cache best-effort
        pass


def _parse_date_obs(date_obs: str) -> Optional[datetime]:
    if not date_obs:
        return None
    s = str(date_obs).strip()
    # Normalize common FITS variants
    s = s.replace("Z", "")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        # Last resort: try trimming subseconds
        try:
            if "." in s:
                s2 = s.split(".")[0]
                dt = datetime.fromisoformat(s2)
            else:
                return None
        except Exception:
            return None
    return dt.replace(tzinfo=timezone.utc)


def extract_site_time_from_fits(fits_path: str | Path) -> Optional[Tuple[datetime, float, float]]:
    fp = Path(fits_path)
    if not fp.exists():
        return None

    # Seestar / astrometry downloads may produce header-only FITS or non-standard cards.
    # ignore_missing_simple=True makes Astropy more tolerant.
    with fits.open(fp, ignore_missing_simple=True) as hdul:
        hdr = hdul[0].header

    lat = hdr.get("SITELAT")
    lon = hdr.get("SITELONG")
    date_obs = hdr.get("DATE-OBS")

    if lat is None or lon is None or date_obs is None:
        return None

    dt = _parse_date_obs(str(date_obs))
    if not dt:
        return None

    try:
        return dt, float(lat), float(lon)
    except Exception:
        return None


def fetch_openmeteo_conditions(dt_utc: datetime, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    # Cache key: hour + rounded lat/lon to reduce duplicates
    hour = dt_utc.replace(minute=0, second=0, microsecond=0)
    key = f"{hour.isoformat()}|{lat:.4f}|{lon:.4f}"

    cache = _load_cache()
    if key in cache:
        return cache[key]

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": hour.date().isoformat(),
        "end_date": hour.date().isoformat(),
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "timezone": "UTC",
    }

    r = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    hours = data.get("hourly", {}) or {}
    times = hours.get("time", []) or []
    if not times:
        return None

    # Find nearest hour index
    def _t(i: int) -> datetime:
        return datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc)

    idx = min(range(len(times)), key=lambda i: abs(_t(i) - hour))

    out = {
        "temperature_c": (hours.get("temperature_2m", [None]) or [None])[idx],
        "humidity_pct": (hours.get("relative_humidity_2m", [None]) or [None])[idx],
        "pressure_hpa": (hours.get("surface_pressure", [None]) or [None])[idx],
        "wind_speed_kmh": (hours.get("wind_speed_10m", [None]) or [None])[idx],
        "wind_dir_deg": (hours.get("wind_direction_10m", [None]) or [None])[idx],
        "datetime_utc": hour.isoformat(),
        "lat": lat,
        "lon": lon,
        "source": "Open-Meteo archive (UTC)",
    }

    cache[key] = out
    _save_cache(cache)
    return out


def render_space_weather_block(fits_path: str | Path) -> str:
    info = extract_site_time_from_fits(fits_path)
    if not info:
        return (
            "<div class='card shadow-sm'>"
            "<div class='card-body text-muted'>"
            "Météo/conditions: données FITS insuffisantes (DATE-OBS/SITELAT/SITELONG)."
            "</div></div>"
        )

    dt, lat, lon = info

    try:
        meteo = fetch_openmeteo_conditions(dt, lat, lon)
    except Exception as e:
        return f"""<div class='card shadow-sm'>
  <div class='card-header'><strong>Météo et conditions d’observation</strong></div>
  <div class='card-body text-muted'>Données météo indisponibles (erreur API): {str(e)}</div>
</div>"""

    if not meteo:
        return """<div class='card shadow-sm'>
  <div class='card-header'><strong>Météo et conditions d’observation</strong></div>
  <div class='card-body text-muted'>Aucune donnée météo trouvée pour cette heure (UTC).</div>
</div>"""

    def fmt(x, suffix: str = "") -> str:
        return f"{x}{suffix}" if x is not None else "N/D"

    return f"""<div class="card shadow-sm">
  <div class="card-header">
    <strong>Météo et conditions d’observation</strong>
    <span class="text-muted small ms-2">({meteo.get('source','')})</span>
  </div>
  <div class="card-body">
    <table class="table table-sm align-middle mb-0">
      <tr><th class="w-50">Date / Heure (UTC)</th><td>{meteo.get('datetime_utc','')}</td></tr>
      <tr><th>Température</th><td>{fmt(meteo.get('temperature_c'), ' °C')}</td></tr>
      <tr><th>Humidité</th><td>{fmt(meteo.get('humidity_pct'), ' %')}</td></tr>
      <tr><th>Pression</th><td>{fmt(meteo.get('pressure_hpa'), ' hPa')}</td></tr>
      <tr><th>Vent</th><td>{fmt(meteo.get('wind_speed_kmh'), ' km/h')} – {fmt(meteo.get('wind_dir_deg'), '°')}</td></tr>
      <tr><th>Site (lat/lon)</th><td>{lat:.4f}, {lon:.4f}</td></tr>
    </table>
  </div>
</div>"""
