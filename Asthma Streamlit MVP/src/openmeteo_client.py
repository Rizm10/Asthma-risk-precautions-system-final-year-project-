import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _get_json(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_openmeteo_current(lat: float, lon: float) -> dict:
    # Weather (current)
    w_params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }
    w = _get_json(WEATHER_URL, w_params)
    wc = (w or {}).get("current") or {}

    # Air quality + pollen (current)
    a_params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": ",".join(
            [
                "european_aqi",
                "pm2_5",
                "nitrogen_dioxide",
                "ozone",
                "alder_pollen",
                "birch_pollen",
                "grass_pollen",
                "mugwort_pollen",
                "olive_pollen",
                "ragweed_pollen",
            ]
        ),
    }
    a = _get_json(AIR_URL, a_params)
    ac = (a or {}).get("current") or {}

    return {
        "time": wc.get("time") or ac.get("time"),
        "temp_c": wc.get("temperature_2m"),
        "rh": wc.get("relative_humidity_2m"),
        "wind": wc.get("wind_speed_10m"),
        "eu_aqi": ac.get("european_aqi"),
        "pm2_5": ac.get("pm2_5"),
        "no2": ac.get("nitrogen_dioxide"),
        "o3": ac.get("ozone"),
        "pollen": {
            "alder": ac.get("alder_pollen"),
            "birch": ac.get("birch_pollen"),
            "grass": ac.get("grass_pollen"),
            "mugwort": ac.get("mugwort_pollen"),
            "olive": ac.get("olive_pollen"),
            "ragweed": ac.get("ragweed_pollen"),
        },
    }
