import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import json

# Fichier source
input_file = "/opt/airflow/data/avis_clean.json"
pipeline_file = "/opt/airflow/app/sentiment_pipeline.joblib"

# Lire JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Créer DataFrame
df = pd.DataFrame(data)

# Vérifier si la colonne 'contenu' existe
if "contenu" not in df.columns:
    raise ValueError("Le fichier doit contenir la colonne 'contenu'.")

# Si pas de label, créer une colonne 'sentiment' fictive pour entraîner le pipeline
if "sentiment" not in df.columns:
    df["sentiment"] = ["positive" if x > 3 else "negative" for x in df.get("nombre_etoile", [5]*len(df))]

# Créer pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression())
])

# Entraîner
pipeline.fit(df["contenu"], df["sentiment"])

# Sauvegarder
joblib.dump(pipeline, pipeline_file)
print(f"Pipeline créé et sauvegardé dans {pipeline_file}")
