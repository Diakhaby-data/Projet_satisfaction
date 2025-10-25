import os
from motor.motor_asyncio import AsyncIOMotorClient

# -----------------------------
# Configuration MongoDB
# -----------------------------
MONGO_USER = os.getenv("MONGO_USER", "dkb")
MONGO_PASS = os.getenv("MONGO_PASS", "diakhaby")
MONGO_DB   = os.getenv("MONGO_DB", "satisfaction")

# Détection automatique de l'environnement
# Si dans Docker avec réseau interne, utiliser le nom du conteneur
# Sinon, utiliser localhost
if os.getenv("DOCKER_ENV", "0") == "1":
    MONGO_HOST = os.getenv("MONGO_HOST", "mongo_service")
else:
    MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")

MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))

# URL de connexion avec authSource=admin si utilisateur admin
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

# -----------------------------
# Création du client et collection
# -----------------------------
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
avis_collection = db["avis"]

# -----------------------------
# Helper pour transformer un document Mongo en dict
# -----------------------------
def avis_helper(avis) -> dict:
    return {
        "id": str(avis.get("_id", "")),
        "titre_avis": avis.get("titre_avis") or avis.get("Titre_avis") or "",
        "contenu": avis.get("contenu") or avis.get("Contenu (texte)") or "",
        "texte_nettoye": avis.get("texte_nettoye", ""),
        "nombre_etoile": avis.get("nombre_etoile") or avis.get("Nombre_etoile") or 0,
        "date_avis": avis.get("date_avis") or avis.get("Date_avis") or "",
        "pays": avis.get("pays") or avis.get("Pays") or "",
        "langue": avis.get("langue") or "",
        "reponse_entreprise": (
            str(avis.get("reponse_entreprise") or avis.get("Reponse_entreprise (OUI/NON)") or "")
            .strip()
            .upper() == "OUI"
        ),
        "texte_entreprise": avis.get("texte_entreprise") or avis.get("Texte_entreprise") or "",
        "date_reponse_entreprise": avis.get("date_reponse_entreprise") or avis.get("Date_reponse_entreprise") or "",
        "prediction_ml": avis.get("prediction_ml") or None
    }

# -----------------------------
# Fonction de test de connexion
# -----------------------------
async def test_connexion():
    try:
        # Ping pour vérifier la connexion
        await client.admin.command("ping")
        count = await avis_collection.count_documents({})
        print(f"✅ Connexion MongoDB réussie, {count} documents dans la collection 'avis'")
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB : {e}")

# -----------------------------
# Exécution directe pour test
# -----------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connexion())
