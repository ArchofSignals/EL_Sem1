import paho.mqtt.client as mqtt
import sqlite3
import time
import math
from datetime import datetime
import computation
import os  # <--- Add this library

# --- CONFIGURATION ---
# Get the folder where THIS python script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force the database to live in that same folder
DB_NAME = os.path.join(BASE_DIR, "factory_data.db")

# --- CONFIGURATION ---
MQTT_BROKER = "localhost"  # Since this script runs on the same laptop as Mosquitto
MQTT_TOPIC = "sensor/vibration"


# Threshold for "Fault Detection" (in m/s^2)
# Normal gravity is ~9.8. If vibration spikes +/- 5m/s^2, we flag it.
FAULT_THRESHOLD = 15.0 

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            acc_x REAL,
            acc_y REAL,
            acc_z REAL,
            total_vibration REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized.")



# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    # print(f"Received: {payload}") # Uncomment to debug raw stream

    # Process Data using computation module
    result = computation.process_data(payload, FAULT_THRESHOLD)
    
    if result:
        x, y, z, vib, status = result
        
        # Store in Database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO readings (timestamp, acc_x, acc_y, acc_z, total_vibration, status) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now(), x, y, z, vib, status)
        )
        conn.commit()
        conn.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    init_db()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to Broker...")
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        # Loop forever, blocking the script to wait for messages
        client.loop_forever()
    except ConnectionRefusedError:
        print("❌ Could not connect to Mosquitto. Is it running?")