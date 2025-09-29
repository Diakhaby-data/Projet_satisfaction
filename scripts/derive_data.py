import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import os

# Créer le dossier reports s'il n'existe pas
os.makedirs("reports", exist_ok=True)

# Connexion MongoDB
client = MongoClient("mongodb://dkb:diakhaby@localhost:27017/")
db = client.satisfaction
avis = pd.DataFrame(list(db.avis.find()))

# normaliser les noms de colonnes en minuscules et sans caractères spéciaux
avis.columns = [c.lower().replace(" ", "_").replace("(", "").replace(")", "") for c in avis.columns]

# Vérifier les colonnes et types
print(avis.dtypes)
print(avis.describe(include='all'))

# Distribution du nombre d'étoiles
avis['nombre_etoile'].value_counts().sort_index().plot(kind='bar', title='Distribution Nombre d\'étoiles')
plt.savefig('reports/distribution_nombre_etoiles.png')

# Distribution par pays
avis['pays'].value_counts().plot(kind='bar', title='Distribution par Pays')
plt.savefig('reports/distribution_pays.png')

print("Rapport généré dans le dossier reports/")
