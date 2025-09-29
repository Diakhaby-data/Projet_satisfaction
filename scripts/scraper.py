import requests
from pymongo import MongoClient
from datetime import datetime
import random

# Connexion MongoDB
client = MongoClient("mongodb://dkb:diakhaby@localhost:27017/")
db = client["satisfaction"]
avis_collection = db["avis"]

def scrape_and_insert():
    # Exemple : récupérer des commentaires d'une API publique
    url = "https://jsonplaceholder.typicode.com/comments"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Erreur scraping {response.status_code}")
        return

    data = response.json()[:20]  # on prend 20 exemples
    documents = []

    for d in data:
        doc = {
            "Titre_avis": f"Avis de {d['name']}",
            "Contenu (texte)": d["body"],
            "Nombre_etoile": random.randint(1, 5),
            "Date_avis": datetime.utcnow(),
            "Pays": random.choice(["FR", "US", "DE", "ES"]),
            "langue": "fr" if random.random() > 0.5 else "en",
            "Reponse_entreprise (OUI/NON)": random.choice(["OUI", "NON"]),
            "Texte_entreprise": None,
            "Date_reponse_entreprise": None,
            "prediction_ml": None
        }
        documents.append(doc)

    if documents:
        avis_collection.insert_many(documents)
        print(f"✅ {len(documents)} avis insérés dans MongoDB")
    else:
        print("⚠️ Aucun avis récupéré")

if __name__ == "__main__":
    scrape_and_insert()
