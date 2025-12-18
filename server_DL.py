import logging
import paho.mqtt.client as mqtt
import sqlite3
import math
import os
from datetime import datetime

# --- CONFIGURATION ---
MQTT_BROKER = "localhost"
MQTT_TOPIC = "sensor/vibration"
DB_NAME = os.path.join(os.path.dirname(__file__), "factory_data.db")

FAULT_THRESHOLD = 15.0  # m/s^2

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            acc_x REAL,
            acc_y REAL,
            acc_z REAL,
            total_vibration REAL,
            status TEXT
        )
    """)
    conn.commit()
    print(f"📁 Database initialized: {DB_NAME}")
    return conn

# --- DATA PROCESSING ---
def process_data(payload):
    try:
        x, y, z = map(float, payload.strip().split(","))
        magnitude = math.sqrt(x*x + y*y + z*z)

        status = "CRITICAL FAULT" if magnitude > FAULT_THRESHOLD else "NORMAL"
        if status == "CRITICAL FAULT":
            print(f"⚠️ FAULT | Magnitude: {magnitude:.2f}")

        return x, y, z, magnitude, status

    except Exception as e:
        print(f"⚠️ Bad payload '{payload}': {e}")
        return None

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT connection failed (rc={reason_code})")

def on_subscribe(client, userdata, mid, reason_codes, properties):
    print(f"📡 Subscribed successfully: {reason_codes}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    result = process_data(payload)

    if not result:
        return

    x, y, z, vib, status = result

    cursor.execute(
        "INSERT INTO readings VALUES (NULL, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), x, y, z, vib, status)
    )
    conn.commit()


   

# --- MAIN ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    conn = init_db()
    cursor = conn.cursor()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe


    print("🔌 Connecting to broker...")
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

