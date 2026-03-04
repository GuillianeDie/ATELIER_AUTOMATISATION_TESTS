from flask import Flask, render_template, jsonify
import requests
import time
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# --- CONFIGURATION ---
TARGET_API = "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true"
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# --- LOGIQUE DE STOCKAGE (SQLite) ---
def init_db():
    """Crée la table des résultats si elle n'existe pas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            status TEXT,
            latency_ms REAL,
            temp_value REAL,
            tests_passed INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_run(status, latency, temp, passed_count):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO runs (timestamp, status, latency_ms, temp_value, tests_passed) 
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, latency, temp, passed_count))
    conn.commit()
    conn.close()

# Initialisation de la base au démarrage
init_db()

# --- MOTEUR DE TESTS (RUNNER) ---
def run_api_tests():
    start_time = time.time()
    response = None
    
    # 1. Robustesse : Timeout 3s + 1 Retry (Section 4B du barème)
    for attempt in range(2):
        try:
            response = requests.get(TARGET_API, timeout=3)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            if attempt == 1: 
                save_run("FAIL", 0, 0, 0)
                return None
    
    latency = round((time.time() - start_time) * 1000, 2)
    data = response.json()
    
    # 2. Plan de tests : 6 assertions (Section 4A du barème)
    tests = [
        response.status_code == 200,                                    # Test 1: Code HTTP 200
        "application/json" in response.headers.get("Content-Type", ""), # Test 2: Format JSON
        "current_weather" in data,                                      # Test 3: Champ présent
        isinstance(data.get("current_weather", {}).get("temperature"), (int, float)), # Test 4: Type Temp
        "windspeed" in data.get("current_weather", {}),                 # Test 5: Champ Vent
        latency < 1000                                                  # Test 6: Performance < 1s
    ]
    
    passed_count = sum(tests)
    final_status = "PASS" if all(tests) else "FAIL"
    temp = data.get("current_weather", {}).get("temperature", 0)
    
    save_run(final_status, latency, temp, passed_count)
    return {
        "status": final_status,
        "latency": latency,
        "temp": temp,
        "passed": passed_count
    }

# --- ROUTES FLASK ---

@app.route("/")
def index():
    """Affiche les consignes du projet"""
    try:
        return render_template('consignes.html')
    except:
        return "Fichier consignes.html introuvable dans /templates."

@app.route("/run")
def trigger_run():
    """Exécute un run de test manuellement"""
    result = run_api_tests()
    if result:
        return jsonify({"message": "Test effectué", "result": result})
    return jsonify({"message": "Erreur critique lors du test"}), 500

@app.route("/status")
def status_page():
    """Affiche le dernier run au format JSON (Indicateurs QoS)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 1')
    last_run = cursor.fetchone()
    conn.close()
    
    if last_run:
        return jsonify({
            "last_test_at": last_run[1],
            "status": last_run[2],
            "latency_ms": last_run[3],
            "temperature_paris": last_run[4],
            "tests_passed_count": last_run[5],
            "tester": "Guilliane"
        })
    return jsonify({"message": "Aucun historique disponible. Allez sur /run"}), 404

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # On récupère les 10 derniers runs
    cursor.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 10')
    history = cursor.fetchall()
    conn.close()
    
    # On passe 'history' au template sous le nom 'runs'
    return render_template('dashboard.html', runs=history)

@app.route("/health")
def health():
    """Vérifie que l'application et la base de données sont OK"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
