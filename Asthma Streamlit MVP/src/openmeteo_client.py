import requests 

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
def fetch_weather_data(lat: float , lon: float):
    w_params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m" }
    
