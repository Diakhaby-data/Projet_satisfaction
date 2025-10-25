import json
import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

# Connexion MongoDB
client = MongoClient("mongodb://dkb:diakhaby@mongo_service:27017/")
db = client["satisfaction"]
collection = db["avis"]

# Récupérer les avis sans sentiment
avis_sans_sentiment = list(collection.find({"sentiment": {"$exists": False}}))

logging.info(f"Analyse de {len(avis_sans_sentiment)} avis")

# Analyse simple basée sur les étoiles
count = 0
for avis in avis_sans_sentiment:
    if avis["nombre_etoile"] >= 4:
        sentiment = "positif"
    elif avis["nombre_etoile"] <= 2:
        sentiment = "negatif"
    else:
        sentiment = "neutre"
    
    collection.update_one(
        {"_id": avis["_id"]},
        {"$set": {"sentiment": sentiment}}
    )
    count += 1

logging.info(f"Analyse de sentiment terminée : {count} avis mis à jour")
