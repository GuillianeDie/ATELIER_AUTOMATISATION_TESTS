# Configuration de l'API cible (Météo Paris)
TARGET_API = "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current_weather=true"

@app.route("/status")
def status():
    """Route de monitoring pour l'API Météo"""
    start_time = time.time()
    
    try:
        response = requests.get(TARGET_API, timeout=5)
        end_time = time.time()
        latency = round((end_time - start_time) * 1000, 2)
        
        # On extrait la température pour vérifier que la donnée est valide
        json_data = response.json()
        temp = json_data.get("current_weather", {}).get("temperature")
        
        data = {
            "service": "Open-Meteo",
            "status": "UP" if response.status_code == 200 else "DOWN",
            "response_time_ms": latency,
            "current_temp_paris": temp,
            "unit": "Celsius",
            "tester": "Guilliane"
        }
    except Exception as e:
        data = {"status": "ERROR", "message": str(e)}

    return jsonify(data)
