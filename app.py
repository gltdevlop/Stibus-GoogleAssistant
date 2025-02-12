from flask import Flask, request, jsonify
from scripts.utils import normalize_text
from scripts.buses import prochain_bus

app = Flask(__name__)

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