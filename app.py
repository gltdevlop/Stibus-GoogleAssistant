from flask import Flask, request, jsonify
import yaml
from datetime import datetime

app = Flask(__name__)

# Charger les horaires depuis les fichiers YAML
def charger_horaires(ligne):
    fichier_yaml = f"Stibus Ligne {ligne} - Semaine.yaml"
    try:
        with open(fichier_yaml, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None

# Fonction pour trouver le prochain bus
def prochain_bus(ligne, arret, direction):
    data = charger_horaires(ligne)
    if not data:
        return f"Les horaires de la ligne {ligne} ne sont pas disponibles."

    key = f"ligne_{ligne}" if ligne.isalpha() else f"ligne_{ligne}"
    if key not in data:
        return f"Aucune donnée pour la ligne {ligne}."

    horaires = None
    for stop in data[key]["arrets"]:
        if stop["nom"].lower() == arret.lower():
            horaires = stop["horaires"].get(f"vers_{direction}")
            break

    if not horaires:
        return f"Aucun horaire trouvé pour {arret} vers {direction}."

    # Convertir l'heure actuelle en datetime
    maintenant = datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")

    # Trouver le premier horaire qui est plus grand que l'heure actuelle
    for heure in horaires:
        heure_bus = datetime.strptime(heure, "%H:%M")
        if heure_bus > maintenant:
            return f"Le prochain bus de la {ligne} à {arret} en direction de {direction} est prévu à {heure}"

    return f"Plus de bus aujourd'hui pour {arret} en direction de {direction}."

# Route pour Dialogflow
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    params = req.get("queryResult", {}).get("parameters", {})

    ligne = params.get("ligne", "").upper()  # Convertir en majuscule pour ligne A, B...
    arret = params.get("arret", "")
    direction = params.get("direction", "")

    if not ligne or not arret or not direction:
        return jsonify({"fulfillmentText": "Merci de remplir tous les champs."})

    reponse = prochain_bus(ligne, arret, direction)
    return jsonify({"fulfillmentText": reponse})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
