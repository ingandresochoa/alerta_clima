import requests
import logging
import pyodbc
from datetime import datetime, timedelta

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = "11.24079"
LONGITUDE = "-74.19904"
PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": "temperature_2m,precipitation,cloudcover,windspeed_10m",
    "timezone": "auto"
}
DB_CONNECTION_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-KPSGVP52;DATABASE=WeatherAlert;UID=LAPTOP-KPSGVP52\\andre;PWD='';"

logging.basicConfig(filename='weather_alerts.log', level=logging.INFO)

def get_db_connection():
    try:
        return pyodbc.connect(DB_CONNECTION_STRING)
    except pyodbc.Error as e:
        logging.error(f"Database connection error: {e}")
        return None
    
def fetch_weather_data():
    try:
        response = requests.get(WEATHER_API_URL, params=PARAMS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Weather API error: {e}")
        return None 

def analyze_weather_data(data):
    try:
        alerts = []
        current_hour = datetime.now().hour
        forecast = data.get("hourly", {})
        
        for i in range(current_hour, current_hour + 1):
            if forecast["precipitation"][i] > 1:
                alerts.append("🌧️ Lluvia pronosticada")
            if forecast["windspeed_10m"][i] > 40:
                alerts.append("🌪️ Vientos fuertes")
            if forecast["cloudcover"][i] > 80:
                alerts.append("☁️ Alta nubosidad")
        
        return list(set(alerts))
    except (KeyError, IndexError) as e:
        logging.error(f"Error in analysis: {e}")
        return []

def main():
    weather_data = fetch_weather_data()
    if not weather_data:
        return
    
    alerts = analyze_weather_data(weather_data)
    
    for alert in alerts:
        print(alert)

    print(get_db_connection)

if __name__ == "__main__":
    main()