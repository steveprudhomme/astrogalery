# space_weather.py
# GNU Astro Galery — Module météo (local + API)
#
# FR:
#  - Extrait DATE-OBS, SITELAT, SITELONG depuis un FITS Seestar S50
#  - Interroge Open‑Meteo (archive API) pour obtenir des conditions météo (UTC)
#  - Retourne un bloc HTML Bootstrap à injecter dans la page objet
#  - Met en cache les réponses pour éviter de re-télécharger inutilement
#
# EN:
#  - Extracts DATE-OBS, SITELAT, SITELONG from a Seestar S50 FITS
#  - Calls Open‑Meteo archive API to fetch weather conditions (UTC)
#  - Returns a Bootstrap HTML block for the object page
#  - Caches results to avoid unnecessary re-downloads

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
        pass


def _parse_date_obs(date_obs: str) -> Optional[datetime]:
    if not date_obs:
        return None
    s = str(date_obs).strip()
    if s.endswith("Z"):
        s = s[:-1]
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        try:
            if "." in s:
                dt = datetime.fromisoformat(s.split(".")[0])
            else:
                return None
        except Exception:
            return None
    return dt.replace(tzinfo=timezone.utc)


def extract_site_time_from_fits(fits_path: str | Path) -> Optional[Tuple[datetime, float, float]]:
    fp = Path(fits_path)
    if not fp.exists():
        return None

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

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        return None

    def t(i: int) -> datetime:
        return datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc)

    idx = min(range(len(times)), key=lambda i: abs(t(i) - hour))

    out = {
        "temperature_c": (hourly.get("temperature_2m") or [None])[idx],
        "humidity_pct": (hourly.get("relative_humidity_2m") or [None])[idx],
        "pressure_hpa": (hourly.get("surface_pressure") or [None])[idx],
        "wind_speed_kmh": (hourly.get("wind_speed_10m") or [None])[idx],
        "wind_dir_deg": (hourly.get("wind_direction_10m") or [None])[idx],
        "datetime_utc": hour.isoformat(),
        "lat": lat,
        "lon": lon,
        "source": "Open‑Meteo archive (UTC)",
    }

    cache[key] = out
    _save_cache(cache)
    return out


def render_space_weather_block(fits_path: str | Path) -> str:
    info = extract_site_time_from_fits(fits_path)
    if not info:
        return (
            "<div class='card shadow-sm'>"
            "<div class='card-header'><strong>Météo et conditions d’observation</strong></div>"
            "<div class='card-body text-muted'>"
            "Données FITS insuffisantes (DATE-OBS/SITELAT/SITELONG)."
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
