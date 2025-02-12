from flask import Flask, request, jsonify
import yaml
from datetime import datetime, timedelta
import unicodedata
import os

app = Flask(__name__)

# Function to normalize text (remove accents, spaces, and convert to lowercase)
def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    text = text.replace(" ", "").replace("'", "").replace("’", "")  # Remove spaces and apostrophes
    return text

# Load schedules from YAML files based on the day of the week
def charger_horaires(ligne, day_offset=0):
    target_day = (datetime.today().weekday() + day_offset) % 7
    
    if target_day == 6:
        return "Bus du dimanche pas encore enregistrés. Visitez https://stibus.fr"
    elif target_day < 5:
        fichier_yaml = f"lines/week/{ligne}.yaml"
    else:
        fichier_yaml = f"lines/sat/{ligne}.yaml"

    try:
        with open(fichier_yaml, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None

# Function to find the next bus
def prochain_bus(ligne, arret, direction):
    data = charger_horaires(ligne)
    if isinstance(data, str):
        return data  # Return message if it's Sunday
    
    if not data:
        return f"Les horaires de la ligne {ligne} ne sont pas disponibles."

    key = f"ligne_{ligne}"  # Key format in YAML file
    if key not in data:
        return f"Aucune donnée pour la ligne {ligne}."

    horaires = None
    
    # Normalize all stop names in YAML before searching
    for stop in data[key]["arrets"]:
        stop_nom_normalized = normalize_text(stop["nom"])
        
        if stop_nom_normalized == normalize_text(arret):
            # Normalize keys for directions in YAML
            direction_key = f"vers_{normalize_text(direction)}"
            
            # Normalize all direction keys to avoid mismatches
            horaires = {normalize_text(k): v for k, v in stop["horaires"].items()}
            
            if direction_key in horaires:
                horaires = horaires[direction_key]
            else:
                horaires = None
            break

    if not horaires:
        return f"Aucun horaire trouvé pour {arret} vers {direction}."

    # Get current time
    maintenant = datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")

    # Find the next available bus
    for heure in horaires:
        heure_bus = datetime.strptime(heure, "%H:%M")
        if heure_bus > maintenant:
            return f"Le prochain bus de la {ligne} à {arret} en direction de {direction} est prévu à {heure}."

    # If no buses left today, check tomorrow's schedule
    data_tomorrow = charger_horaires(ligne, day_offset=1)
    if not data_tomorrow or key not in data_tomorrow:
        return f"Aucun horaire disponible pour demain."
    
    for stop in data_tomorrow[key]["arrets"]:
        stop_nom_normalized = normalize_text(stop["nom"])
        if stop_nom_normalized == normalize_text(arret):
            direction_key = f"vers_{normalize_text(direction)}"
            horaires_tomorrow = {normalize_text(k): v for k, v in stop["horaires"].items()}
            if direction_key in horaires_tomorrow:
                horaires_tomorrow = horaires_tomorrow[direction_key]
                if horaires_tomorrow:
                    return f"Le prochain bus de la {ligne} à {arret} en direction de {direction} est demain à {horaires_tomorrow[0]}."
    
    return f"Aucun bus disponible demain non plus pour {arret} en direction de {direction}."

# Webhook route for Dialogflow
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    ligne = normalize_text(params.get("ligne", "").upper())  # Convert to uppercase for letters like A, B...
    arret = normalize_text(params.get("arret", ""))
    direction = normalize_text(params.get("direction", ""))

    if not ligne or not arret or not direction:
        return jsonify({"fulfillmentText": "Merci de remplir tous les champs."})

    reponse = prochain_bus(ligne, arret, direction)
    return jsonify({"fulfillmentText": reponse})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
