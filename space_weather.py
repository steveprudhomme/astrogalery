
# space_weather.py
# Module ajouté à GNU Astro Galery
# Version compatible avec 00.00.07
#
# Ce module extrait les coordonnées et l'heure depuis les headers FITS
# (SITELAT / SITELONG / DATE-OBS) et interroge Open-Meteo pour obtenir :
# - Température
# - Humidité
# - Pression
# - Vent (vitesse et direction)
#
# Le bloc retourné est prêt à être injecté dans la page objet.

import requests
from datetime import datetime, timezone
from astropy.io import fits

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

def extract_site_time_from_fits(fits_path):
    with fits.open(fits_path) as hdul:
        hdr = hdul[0].header

        lat = hdr.get("SITELAT")
        lon = hdr.get("SITELONG")
        date_obs = hdr.get("DATE-OBS")

        if lat is None or lon is None or date_obs is None:
            return None

        dt = datetime.fromisoformat(date_obs.replace("Z", "")).replace(tzinfo=timezone.utc)
        return dt, float(lat), float(lon)


def fetch_openmeteo_conditions(dt_utc, lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": dt_utc.date().isoformat(),
        "end_date": dt_utc.date().isoformat(),
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

    hours = data.get("hourly", {})
    times = hours.get("time", [])

    if not times:
        return None

    target_hour = dt_utc.replace(minute=0, second=0)
    idx = min(range(len(times)), key=lambda i: abs(
        datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc) - target_hour
    ))

    return {
        "temperature_c": hours["temperature_2m"][idx],
        "humidity_pct": hours["relative_humidity_2m"][idx],
        "pressure_hpa": hours["surface_pressure"][idx],
        "wind_speed_kmh": hours["wind_speed_10m"][idx],
        "wind_dir_deg": hours["wind_direction_10m"][idx],
    }


def render_space_weather_block(fits_path):
    info = extract_site_time_from_fits(fits_path)
    if not info:
        return "<p>Données météo non disponibles.</p>"

    dt, lat, lon = info
    meteo = fetch_openmeteo_conditions(dt, lat, lon)

    if not meteo:
        return "<p>Données météo non disponibles.</p>"

    return f"""
    <div class="card my-4">
      <div class="card-header">
        <strong>Météo et conditions d’observation</strong>
      </div>
      <div class="card-body">
        <table class="table table-sm">
          <tr><th>Date / Heure (UTC)</th><td>{dt.isoformat()}</td></tr>
          <tr><th>Température</th><td>{meteo['temperature_c']} °C</td></tr>
          <tr><th>Humidité</th><td>{meteo['humidity_pct']} %</td></tr>
          <tr><th>Pression</th><td>{meteo['pressure_hpa']} hPa</td></tr>
          <tr><th>Vent</th><td>{meteo['wind_speed_kmh']} km/h – {meteo['wind_dir_deg']}°</td></tr>
        </table>
      </div>
    </div>
    """
