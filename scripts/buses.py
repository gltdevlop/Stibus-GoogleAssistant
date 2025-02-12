from scripts.loader import charger_horaires
from scripts.utils import normalize_text
from datetime import datetime

# Load schedules from YAML files based on the day of the week
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
