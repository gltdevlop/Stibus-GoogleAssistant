from flask import Flask, request, jsonify
import yaml
from datetime import datetime
import unicodedata

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
    arret_nom_yaml = None  # Store the exact name from YAML
    ligne_nom_yaml = data[key].get("nom", ligne)  # Get the exact line name from YAML
    direction_nom_yaml = None  # Store the exact direction name from YAML
    
    # Find the correct stop and normalize all stop names in YAML before searching
    for stop in data[key]["arrets"]:
        stop_nom_normalized = normalize_text(stop["nom"])
        
        if stop_nom_normalized == normalize_text(arret):
            arret_nom_yaml = stop["nom"]  # Store the exact YAML stop name
            
            # Normalize all direction keys to avoid mismatches
            horaires = {normalize_text(k): v for k, v in stop["horaires"].items()}
            
            for dir_key in stop["horaires"].keys():
                if normalize_text(dir_key) == f"vers_{normalize_text(direction)}":
                    direction_nom_yaml = dir_key.replace("vers_", "")
                    horaires = horaires[normalize_text(dir_key)]
                    break
            
            if direction_nom_yaml:
                break
            else:
                horaires = None
    
    if not horaires:
        return f"Aucun horaire trouvé pour {arret} vers {direction}."

    # Get current time
    maintenant = datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")

    # Find the next available bus
    for heure in horaires:
        heure_bus = datetime.strptime(heure, "%H:%M")
        if heure_bus > maintenant:
            return f"Le prochain bus de la ligne {ligne_nom_yaml} à l'arrêt {arret_nom_yaml} en direction de {direction_nom_yaml} est prévu à {heure}."

    # If no buses left today, check tomorrow's schedule
    data_tomorrow = charger_horaires(ligne, day_offset=1)
    if not data_tomorrow or key not in data_tomorrow:
        return f"Aucun horaire disponible pour demain."
    
    for stop in data_tomorrow[key]["arrets"]:
        stop_nom_normalized = normalize_text(stop["nom"])
        if stop_nom_normalized == normalize_text(arret):
            for dir_key in stop["horaires"].keys():
                if normalize_text(dir_key) == f"vers_{normalize_text(direction)}":
                    direction_nom_yaml = dir_key.replace("vers_", "")
                    horaires_tomorrow = stop["horaires"][dir_key]
                    if horaires_tomorrow:
                        return f"Le prochain bus de la ligne {ligne_nom_yaml} à l'arrêt {stop['nom']} en direction de {direction_nom_yaml} est demain à {horaires_tomorrow[0]}."
    
    return f"Aucun bus disponible demain non plus pour {arret_nom_yaml} en direction de {direction_nom_yaml}."

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