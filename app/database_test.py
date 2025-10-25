import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# -----------------------------
# Configuration MongoDB avec valeurs par défaut
# -----------------------------
MONGO_USER = os.getenv('MONGO_USER', 'dkb')
MONGO_PASS = os.getenv('MONGO_PASS', 'diakhaby')
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo_service')  # nom du conteneur MongoDB
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB   = os.getenv('MONGO_DB', 'satisfaction')

# URL de connexion avec authSource=admin si utilisateur/admin
MONGO_URL = f'mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin'

# Création du client et de la DB
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]

# -----------------------------
# Fonction de test de connexion
# -----------------------------
async def test_connexion():
    try:
        await client.admin.command('ping')
        count = await db['avis'].count_documents({})
        print(f'✅ Connexion réussie ! {count} documents trouvés dans la collection "avis".')
    except Exception as e:
        print(f'❌ Erreur de connexion MongoDB : {e}')

# -----------------------------
# Exécution directe
# -----------------------------
if __name__ == "__main__":
    asyncio.run(test_connexion())
