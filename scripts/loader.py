import yaml
from datetime import datetime

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