import asyncio
from app.database import avis_collection

async def test_connexion():
    try:
        count = await avis_collection.count_documents({})
        print(f"Connexion réussie — Nombre d'avis dans la collection : {count}")
    except Exception as e:
        print(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    asyncio.run(test_connexion())
