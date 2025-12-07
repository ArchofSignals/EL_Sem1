import paho.mqtt.client as mqtt
import sqlite3
import time
import math
from datetime import datetime

# --- CONFIGURATION ---
MQTT_BROKER = "localhost"  # Since this script runs on the same laptop as Mosquitto
MQTT_TOPIC = "sensor/vibration"
DB_NAME = "factory_data.db"

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

# --- COMPUTATION LOGIC ---
def process_data(payload):
    try:
        # 1. Parse string "x,y,z" into floats
        parts = payload.split(',')
        x = float(parts[0])
        y = float(parts[1])
        z = float(parts[2])

        # 2. Compute Total Acceleration Vector (Pythagoras theorem)
        # Vector Magnitude = sqrt(x^2 + y^2 + z^2)
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        # 3. Simple Fault Logic
        # If the machine is still, magnitude is ~9.8 (Gravity). 
        # Strong vibration pushes this much higher.
        status = "NORMAL"
        if magnitude > FAULT_THRESHOLD:
            status = "CRITICAL FAULT"
            print(f"⚠️ FAULT DETECTED! Magnitude: {magnitude:.2f} m/s^2")

        return x, y, z, magnitude, status

    except Exception as e:
        print(f"Error processing data: {e}")
        return None

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    # print(f"Received: {payload}") # Uncomment to debug raw stream

    # Process Data
    result = process_data(payload)
    
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