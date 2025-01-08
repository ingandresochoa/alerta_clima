import requests
import logging
import mysql.connector
import os

from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
ENV_TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
ENV_TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
ENV_TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

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
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME
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
            OR DATE_ADD(NOW(), INTERVAL -1 HOUR) > last_alert
        """)
        return [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as e:
        logging.error(f"Error getting users: {e}")
        return []
    finally:
        conn.close()

def update_alert_status(phone_number, alert_text, status):
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alert_log (phone_number, alert_text, sent_time, status)
            VALUES (%s, %s, NOW(), %s)
        """, (phone_number, alert_text, status))
        
        if status == 'SUCCESS':
            cursor.execute("""
                UPDATE contacts 
                SET last_alert = NOW()
                WHERE phone_number = %s
            """, (phone_number,))
        
        conn.commit()
    except mysql.connector.Error as e:
        logging.error(f"Error updating status: {e}")
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
            if forecast["windspeed_10m"][i] > 45:
                alerts.append("🌪️ Vientos fuertes")
            if forecast["cloudcover"][i] > 75:
                alerts.append("☁️ Alta nubosidad")
        
        return list(set(alerts))
    except (KeyError, IndexError) as e:
        logging.error(f"Error in analysis: {e}")
        return []
    
def send_sms(message, phone_numbers):
    from twilio.rest import Client

    TWILIO_ACCOUNT_SID = ENV_TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN = ENV_TWILIO_AUTH_TOKEN
    TWILIO_PHONE_NUMBER = ENV_TWILIO_PHONE_NUMBER

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    for phone_number in phone_numbers:
        print(phone_number)
        try:
            message_response = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            status = 'SUCCESS'
            update_alert_status(phone_number, message, status)
        except Exception as e:
            logging.error(f"Twilio error {phone_number}: {e}")
            update_alert_status(phone_number, message, 'FAILED')

def main():
    if not setup_database():
        return
    
    weather_data = fetch_weather_data()
    if not weather_data:
        return
    
    alerts = analyze_weather_data(weather_data)
    if not alerts:
        return

    phone_numbers = get_eligible_users()
    if not phone_numbers:
        return
    
    for alert in alerts:
        send_sms(alert, phone_numbers)

if __name__ == "__main__":
    main()