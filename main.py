import requests

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = "11.24079"
LONGITUDE = "-74.19904"
PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": "temperature_2m,precipitation,cloudcover,windspeed_10m",
    "timezone": "auto"
}

def test_weather_api():
    try:
        response = requests.get(WEATHER_API_URL, params=PARAMS, timeout=10)
        response.raise_for_status()
        data = response.json()

        # --- response data ---
        print(data)
    except requests.RequestException as e:
        print(f"Error al consultar la API: {e}")

if __name__ == "__main__":
    test_weather_api()