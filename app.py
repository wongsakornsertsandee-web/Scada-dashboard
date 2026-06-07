from flask import Flask, render_template, jsonify
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

DB_NAME = "scada_data.db"

PARAMS = {
    "latitude": 60.1695,
    "longitude": 24.9354,
    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
    "timezone": "Europe/Helsinki"
}

event_history = []


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            precipitation REAL,
            heater_status TEXT,
            ventilation_status TEXT,
            weather_alarm TEXT
        )
    """)

    conn.commit()
    conn.close()


def fetch_from_api():
    response = requests.get(OPEN_METEO_URL, params=PARAMS, timeout=10)
    response.raise_for_status()

    api_data = response.json()
    current = api_data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    precipitation = current["precipitation"]

    return {
        "time": current["time"],
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "precipitation": precipitation
    }


def apply_control_logic(data):
    temperature = data["temperature"]
    humidity = data["humidity"]
    wind_speed = data["wind_speed"]
    precipitation = data["precipitation"]

    data["heater_status"] = "ON" if temperature < 18 else "OFF"
    data["ventilation_status"] = "ON" if humidity > 70 else "OFF"
    data["weather_alarm"] = "ON" if wind_speed > 15 or precipitation > 5 else "OFF"

    return data


def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO weather_log (
            timestamp,
            temperature,
            humidity,
            wind_speed,
            precipitation,
            heater_status,
            ventilation_status,
            weather_alarm
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["time"],
        data["temperature"],
        data["humidity"],
        data["wind_speed"],
        data["precipitation"],
        data["heater_status"],
        data["ventilation_status"],
        data["weather_alarm"]
    ))

    conn.commit()
    conn.close()


def get_latest_db_record():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            timestamp,
            temperature,
            humidity,
            wind_speed,
            precipitation,
            heater_status,
            ventilation_status,
            weather_alarm
        FROM weather_log
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "time": row[0],
        "temperature": row[1],
        "humidity": row[2],
        "wind_speed": row[3],
        "precipitation": row[4],
        "heater_status": row[5],
        "ventilation_status": row[6],
        "weather_alarm": row[7]
    }


def get_history(limit=50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            timestamp,
            temperature,
            humidity,
            wind_speed,
            precipitation,
            heater_status,
            ventilation_status,
            weather_alarm
        FROM weather_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "time": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "wind_speed": row[3],
            "precipitation": row[4],
            "heater_status": row[5],
            "ventilation_status": row[6],
            "weather_alarm": row[7]
        })

    return list(reversed(history))


def log_event(device, status):
    now = datetime.now().strftime("%H:%M:%S")

    event = {
        "time": now,
        "device": device,
        "status": status
    }

    if len(event_history) == 0:
        event_history.append(event)
        return

    last_event = event_history[-1]

    if last_event["device"] != device or last_event["status"] != status:
        event_history.append(event)

    if len(event_history) > 50:
        event_history.pop(0)


def get_weather_data():
    data = fetch_from_api()
    data = apply_control_logic(data)

    save_to_db(data)

    log_event("Heater", data["heater_status"])
    log_event("Ventilation", data["ventilation_status"])
    log_event("Weather Alarm", data["weather_alarm"])

    data["events"] = event_history[-10:]

    return data


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/verify")
def verify_page():
    return render_template("verify.html")


@app.route("/api/data")
def api_data():
    try:
        return jsonify(get_weather_data())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def api_history():
    try:
        return jsonify(get_history(50))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/verify")
def api_verify():
    try:
        api_now = get_weather_data()
        db_latest = get_history(1)

        if len(db_latest) == 0:
            return jsonify({
                "status": "NO_DATABASE_DATA",
                "message": "No data found in database yet.",
                "api_now": api_now,
                "db_latest": None
            })

        db_latest = db_latest[-1]

        match_result = {
            "time": api_now["time"] == db_latest["time"],
            "temperature": api_now["temperature"] == db_latest["temperature"],
            "humidity": api_now["humidity"] == db_latest["humidity"],
            "wind_speed": api_now["wind_speed"] == db_latest["wind_speed"],
            "precipitation": api_now["precipitation"] == db_latest["precipitation"],
            "heater_status": api_now["heater_status"] == db_latest["heater_status"],
            "ventilation_status": api_now["ventilation_status"] == db_latest["ventilation_status"],
            "weather_alarm": api_now["weather_alarm"] == db_latest["weather_alarm"]
        }

        return jsonify({
            "status": "MATCH" if all(match_result.values()) else "NOT_MATCH",
            "api_now": api_now,
            "db_latest": db_latest,
            "match_result": match_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)