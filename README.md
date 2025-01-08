# Weather Alerts

Este proyecto, pensado e ideado luego de ver como llovía sábado, domingo y lunes más de 10 horas... proporciona un sistema para enviar alertas meteorologicas a través de SMS, basado en condiciones climáticas como lluvia, vientos fuertes y nubosidad. Utiliza la API de Open Meteo para obtener pronósticos meteorológicos, almacena usuarios y registros en una base de datos MySQL y envía notificaciones SMS a los usuarios utilizando Twilio.

## Funcionalidades

- **Obtención de pronóstico meteorológico**: Consulta las condiciones meteorológicas para la ubicación especificada.
- **Generación de alertas**: Basado en las condiciones meteorológicas, genera alertas para lluvia, vientos fuertes y nubosidad.
- **Envío de alertas por SMS**: Envía alertas a los usuarios registrados mediante Twilio.
- **Gestión de usuarios y alertas**: Los usuarios deben estar registrados en la base de datos MySQL y se actualizan con el estado de las alertas enviadas.

## Tecnologías

- **Python**: Lenguaje de programación principal.
- **Open Meteo API**: API para obtener el pronóstico del tiempo.
- **Twilio**: Plataforma de mensajería para el envío de SMS.
- **MySQL**: Base de datos para almacenar la información de los usuarios y el historial de alertas.

## Instalación

### 1. Clona este repositorio

```bash
git clone https://github.com/tu_usuario/weather-alerts.git
cd weather-alerts

### 2. Instala las dependencias

```bash
pip install -r requirements.txt

### 3. Configura las credenciales

Crea un archivo .env en la raiz del proyceto y agrega las siguientes variables:
```bash
DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="tu_contraseña"
DB_NAME="weather_alerts"
TWILIO_ACCOUNT_SID="tu_sid_de_twilio"
TWILIO_AUTH_TOKEN="tu_token_de_autenticacion_de_twilio"
TWILIO_PHONE_NUMBER="tu_numero_de_twilio"

### 4. Configura la base de datos

Asegúrate de tener la base de datos MySQL configurada y ejecutándose. El nombre de la base de datos debe coincidir con el valor de la variable DB_NAME en el archivo .env. El proyecto creará las tablas necesarias al ejecutarse por primera vez.

## Uso

El sistema se ejecuta automaticamente cuando inicias el script principal. Esto verificará las condiciones meteorologicas y enviará alertas a los usuarios registrados que no hayan recibido una alerta dentro de los pasados 60 minutos.

```bash
python main.py

## Ver los registros

El sistema genera registros de todas las alertas enviadas y errores en el archivo weather_alerts.log.
