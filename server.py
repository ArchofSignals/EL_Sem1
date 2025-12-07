# server.py (Upgraded with Frontend)
from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

DB = 'plant_data.db'
app = Flask(__name__)

# --- HTML TEMPLATE (The Frontend) ---
# This is a simple webpage with CSS styling
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌱 Plant Monitor Dashboard</title>
    <meta http-equiv="refresh" content="5"> <style>
        body { font-family: sans-serif; padding: 20px; background: #f4f4f9; }
        h1 { color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px;}
    </style>
</head>
<body>
    <h1>🌱 Smart Plant Monitor</h1>
    
    <div class="card">
        <h3>Current Status</h3>
        <p><b>Latest Update:</b> {{ latest[1] }}</p>
        <p><b>Temperature:</b> {{ latest[3] }} °C</p>
        <p><b>Humidity:</b> {{ latest[4] }} %</p>
        <p><b>Soil Moisture:</b> {{ latest[6] }} %</p>
    </div>

    <h3>History (Last 10 Readings)</h3>
    <table>
        <tr>
            <th>Time</th>
            <th>Device</th>
            <th>Temp (°C)</th>
            <th>Hum (%)</th>
            <th>Soil (%)</th>
        </tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
            <td>{{ row[6] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ts TEXT, device TEXT, temperature REAL, 
                 humidity REAL, soil_adc INTEGER, soil_percent INTEGER)''')
    conn.commit()
    conn.close()

# --- BACKEND API (Receives Data) ---
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json(force=True)
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        device = data.get('device', 'ESP32')
        temp = data.get('temperature', 0)
        hum = data.get('humidity', 0)
        soil_adc = data.get('soil_adc', 0)
        soil_percent = data.get('soil_percent', 0)

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('INSERT INTO readings (ts, device, temperature, humidity, soil_adc, soil_percent) VALUES (?,?,?,?,?,?)',
                  (ts, device, temp, hum, soil_adc, soil_percent))
        conn.commit()
        conn.close()
        print(f"✅ Data Saved: T={temp} H={hum} S={soil_percent}%") # Console log
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error'}), 400

# --- FRONTEND ROUTE (Shows Data) ---
@app.route('/', methods=['GET'])
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Get the last 10 readings, newest first
    c.execute('SELECT * FROM readings ORDER BY id DESC LIMIT 10')
    rows = c.fetchall()
    conn.close()
    
    # Get the very latest reading for the "Current Status" card
    latest = rows[0] if rows else ['N/A']*7
    
    return render_template_string(HTML_PAGE, rows=rows, latest=latest)

if __name__ == '__main__':
    init_db()
    # host='0.0.0.0' allows access from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=True)