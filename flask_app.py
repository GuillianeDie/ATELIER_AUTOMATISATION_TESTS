from flask import Flask, render_template, jsonify
import requests
import time

app = Flask(__name__)

# Configuration de l'API cible pour le test
TARGET_API = "https://jsonplaceholder.typicode.com/posts/1"

@app.route("/")
def consignes():
    """Affiche la page des consignes (votre code d'origine)"""
    return render_template('consignes.html')

@app.route("/status")
def status():
    """Route de monitoring pour l'ingénieur qualité"""
    start_time = time.time()
    
    try:
        # Exécution du test (SLA / Disponibilité)
        response = requests.get(TARGET_API, timeout=5)
        end_time = time.time()
        
        # Calcul de la latence en millisecondes
        latency = round((end_time - start_time) * 1000, 2)
        
        # Construction des indicateurs de qualité
        data = {
            "api_url": TARGET_API,
            "available": response.status_code == 200,
            "http_status": response.status_code,
            "response_time_ms": latency,
            "content_type": response.headers.get("Content-Type"),
            "tester_alias": "Guilliane"
        }
    except Exception as e:
        # En cas de timeout ou d'erreur réseau
        data = {
            "available": False,
            "error": str(e),
            "response_time_ms": 0
        }

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
