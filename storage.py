import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            status TEXT,
            latency_ms REAL,
            temp_value REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_run(status, latency, temp):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO runs (timestamp, status, latency_ms, temp_value) VALUES (?, ?, ?, ?)',
                   (datetime.now().isoformat(), status, latency, temp))
    conn.commit()
    conn.close()

def get_runs():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return rows
