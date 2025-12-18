from flask import Flask, render_template, jsonify
import sqlite3
import os


DB_NAME = r"d:\Dao of Bits\EL_Sem1\factory_data.db"



app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, total_vibration, status
        FROM readings
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()
    conn.close()

    return jsonify([
        dict(row) for row in reversed(rows)
    ])

if __name__ == '__main__':
    print("Using DB:", DB_NAME)
    print("DB exists:", os.path.exists(DB_NAME))
    app.run(debug=True, host='0.0.0.0', port=5000)

    

