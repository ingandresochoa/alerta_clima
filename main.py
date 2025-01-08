import requests
import logging
import mysql.connector
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
DB_CONNECTION_STRING = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'weather_alerts'
}

logging.basicConfig(filename='weather_alerts.log', level=logging.INFO)
    
def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONNECTION_STRING)
    except mysql.connector.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def setup_database():
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50),
                phone_number VARCHAR(20) UNIQUE,
                last_alert DATETIME
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone_number VARCHAR(20),
                alert_text TEXT,
                sent_time DATETIME,
                status VARCHAR(20)
            )
        """)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        logging.error(f"Error in setup_database: {e}")
        return False
    finally:
        conn.close()

def get_eligible_users():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT phone_number 
            FROM contacts 
            WHERE last_alert IS NULL 
            OR DATE_ADD(NOW(), INTERVAL -3 HOUR) > last_alert
        """)
        return [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        logging.error(f"Error getting users: {e}")
        return []
    finally:
        conn.close()

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
    if not setup_database():
        return
    
    weather_data = fetch_weather_data()
    if not weather_data:
        return
    
    alerts = analyze_weather_data(weather_data)

    phone_numbers = get_eligible_users()
    print(phone_numbers)
    
    for alert in alerts:
        print(alert)

if __name__ == "__main__":
    main()