from flask import Flask, render_template, jsonify
import sqlite3
import os  # <--- Add this library

# --- CONFIGURATION ---


# Force the database to live in that same folder
DB_NAME = os.path.join("d:\Dao of Bits\EL_Sem1", "factory_data.db")

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    # Fetch the latest 50 readings for the live graph
    conn = get_db_connection()
    readings = conn.execute('SELECT * FROM readings ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()

    # Convert to list of dicts and reverse (so graph flows Left -> Right)
    data_list = []
    for row in reversed(readings):
        data_list.append({
            'id': row['id'],
            'timestamp': row['timestamp'],
            'total_vibration': row['total_vibration'],
            'status': row['status']
        })
    
    return jsonify(data_list)

if __name__ == '__main__':
    # Run on port 5000, accessible to your network
    app.run(debug=True, host='0.0.0.0', port=5000)