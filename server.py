# server.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

DB = 'plant_data.db'
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ts TEXT,
                 device TEXT,
                 temperature REAL,
                 humidity REAL,
                 soil_adc INTEGER,
                 soil_percent INTEGER
                 )''')
    conn.commit()
    conn.close()

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json(force=True)
    ts = datetime.now().isoformat()
    device = data.get('device', 'unknown')
    temp = data.get('temperature', None)
    hum = data.get('humidity', None)
    soil_adc = data.get('soil_adc', None)
    soil_percent = data.get('soil_percent', None)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO readings (ts, device, temperature, humidity, soil_adc, soil_percent) VALUES (?,?,?,?,?,?)',
              (ts, device, temp, hum, soil_adc, soil_percent))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
