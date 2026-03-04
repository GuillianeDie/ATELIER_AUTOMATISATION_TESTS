from flask import Flask, render_template, jsonify
import requests
import time

app = Flask(__name__)

# API Météo (Paris)
TARGET_API = "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true"

@app.route("/")
def consignes():
    # Note : assure-toi que le dossier 'templates' contient bien 'consignes.html'
    try:
        return render_template('consignes.html')
    except:
        return "Fichier consignes.html introuvable, mais le serveur fonctionne !"

@app.route("/status")
def status():
    start_time = time.time()
    try:
        response = requests.get(TARGET_API, timeout=5)
        latency = round((time.time() - start_time) * 1000, 2)
        
        # Vérification des données
        json_data = response.json()
        temp = json_data.get("current_weather", {}).get("temperature")
        
        return jsonify({
            "service": "Open-Meteo",
            "status": "UP" if response.status_code == 200 else "DOWN",
            "http_code": response.status_code,
            "response_time_ms": latency,
            "data": {
                "temperature_paris": temp,
                "unit": "celsius"
            },
            "tester": "Guilliane"
        })
    except Exception as e:
        return jsonify({
            "status": "DOWN",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
