import mysql.connector
from pymongo import MongoClient
from datetime import datetime

# Utils
def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)
    except Exception:
        return None

# MongoDB
mongo_client = MongoClient("mongodb://dkb:diakhaby@localhost:27017/projet?authSource=admin")
mongo_db = mongo_client.projet
reviews_cursor = mongo_db.reviews.find({}, {
    "langue": 1,
    "Nombre_etoile": 1,
    "Contenu (texte)": 1,
    "Reponse_entreprise (OUI/NON)": 1,
    "Date_avis": 1
})

# MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="dkb",
    password="diakhaby",
    database="projet"
)
cursor = mysql_conn.cursor(buffered=True)

insert_sql = """
INSERT INTO AvisClients (langue, Nombre_etoile, commentaire, Reponse_entreprise, date_avis)
VALUES (%s, %s, %s, %s, %s)
"""

batch = []
BATCH_SIZE = 1000
count = 0

for doc in reviews_cursor:
    langue = doc.get("langue")
    nb_etoile = doc.get("Nombre_etoile")
    commentaire = doc.get("Contenu (texte)", "")
    rep_entreprise = 1 if doc.get("Reponse_entreprise (OUI/NON)", "NON") == "OUI" else 0
    date_avis = parse_datetime(doc.get("Date_avis"))

    batch.append((langue, nb_etoile, commentaire, rep_entreprise, date_avis))
    if len(batch) >= BATCH_SIZE:
        cursor.executemany(insert_sql, batch)
        mysql_conn.commit()
        count += len(batch)
        batch.clear()

# finir le reste
if batch:
    cursor.executemany(insert_sql, batch)
    mysql_conn.commit()
    count += len(batch)

cursor.close()
mysql_conn.close()
print(f"Ingestion terminée: {count} avis insérés.")
