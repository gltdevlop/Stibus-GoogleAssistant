import yaml
from datetime import datetime

# Charger les horaires depuis le fichier YAML
with open("Stibus Ligne 21 - Semaine.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

def prochain_bus(arret, direction):
    """ Trouve le prochain bus pour un arrêt donné """
    horaires = None
    for stop in data["ligne_21"]["arrets"]:
        if stop["nom"] == arret:
            horaires = stop["horaires"].get(f"vers_{direction}")
            break

    if not horaires:
        return f"Aucun horaire trouvé pour {arret} vers {direction}"

    # Trouver le prochain horaire après l'heure actuelle
    maintenant = datetime.now().strftime("%H:%M")
    for heure in horaires:
        if heure > maintenant:
            return f"Le prochain bus à {arret} vers {direction} est à {heure}"

    return f"Plus de bus aujourd'hui pour {arret} vers {direction}."

# Exemple d'utilisation
arret_demande = input("Arret demandé : ")
direction_demande = input("Direction (vers X) : ")
print(prochain_bus(arret_demande, direction_demande))
