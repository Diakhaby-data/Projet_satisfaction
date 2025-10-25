import mysql.connector
from pymongo import MongoClient
from datetime import datetime

# 1. Connexion à MongoDB

mongo_client = MongoClient(
    "mongodb://dkb:diakhaby@localhost:27017/projet?authSource=admin"
)
mongo_db = mongo_client.projet
reviews_cursor = mongo_db.reviews.find()

# 2. Connexion à MySQL

mysql_conn = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="dkb",
    password="diakhaby",
    database="projet"
)
cursor = mysql_conn.cursor(buffered=True)

# 3. Fonctions utilitaires

def parse_datetime(dt_str):
    """Convertit une date ISO 8601 en datetime Python pour MySQL."""
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)  # MySQL DATETIME n'accepte pas le timezone
    except:
        return datetime.now()

# 4. Insertion des avis

for doc in reviews_cursor:
    titre = doc.get("Titre_avis", "")
    contenu = doc.get("Contenu (texte)", "")
    nb_etoile = doc.get("Nombre_etoile", 0)
    date_avis = parse_datetime(doc.get("Date_avis"))
    pays = doc.get("Pays", None)
    langue = doc.get("langue", None)
    reponse = 1 if doc.get("Reponse_entreprise (OUI/NON)", "NON") == "OUI" else 0
    texte_entreprise = doc.get("Texte_entreprise", "")
    date_reponse = parse_datetime(doc.get("Date_reponse_entreprise"))
    mongo_id = str(doc.get("_id"))

    cursor.execute("""
        INSERT INTO AvisClients 
        (hash, Titre_avis, Contenu, Nombre_etoile, Date_avis, Pays, langue, Reponse_entreprise, Texte_entreprise, Date_reponse_entreprise, mongo_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE hash=hash
    """, (mongo_id, titre, contenu, nb_etoile, date_avis, pays, langue, reponse, texte_entreprise, date_reponse, mongo_id))

# 5. Commit et fermeture

mysql_conn.commit()
cursor.close()
mysql_conn.close()

print("Ingestion des avis terminée !")
