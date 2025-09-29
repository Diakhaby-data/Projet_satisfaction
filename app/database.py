import os
from motor.motor_asyncio import AsyncIOMotorClient

# -----------------------------
# Connexion MongoDB avec authentification
# -----------------------------
MONGO_USER = os.getenv("MONGO_USER", "dkb")
MONGO_PASS = os.getenv("MONGO_PASS", "diakhaby")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB   = os.getenv("MONGO_DB", "satisfaction")

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
avis_collection = db["avis"]

# -----------------------------
# Helper pour transformer un document Mongo en dict
# -----------------------------
def avis_helper(avis) -> dict:
    return {
        "id": str(avis.get("_id")),
        "titre_avis": avis.get("titre_avis") or avis.get("Titre_avis"),
        "contenu_texte": avis.get("contenu_texte") or avis.get("Contenu (texte)"),
        "texte_nettoye": avis.get("texte_nettoye", ""),
        "nombre_etoile": avis.get("nombre_etoile") or avis.get("Nombre_etoile"),
        "date_avis": avis.get("date_avis") or avis.get("Date_avis"),
        "pays": avis.get("pays") or avis.get("Pays"),
        "langue": avis.get("langue"),
        "reponse_entreprise": avis.get("reponse_entreprise") 
                              if "reponse_entreprise" in avis 
                              else avis.get("Reponse_entreprise (OUI/NON)") == "OUI",
        "texte_entreprise": avis.get("texte_entreprise") or avis.get("Texte_entreprise"),
        "date_reponse_entreprise": avis.get("date_reponse_entreprise") or avis.get("Date_reponse_entreprise"),
        "prediction_ml": avis.get("prediction_ml")
    }
