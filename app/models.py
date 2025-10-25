# app/models.py
"""
Module ML extrait du notebook `Projet_analyse_sentiments_ML.ipynb`.

Fonctions exposées :
- clean_text(txt) -> str
- build_pipeline() -> sklearn Pipeline
- train_pipeline(X, y, save_path=..., save=True) -> fitted pipeline
- save_pipeline(pipe, path)
- load_pipeline(path) -> pipeline or None
- predict(texts, pipeline_path=..., train_if_missing=False, data_paths=None) -> dict {preds, probs (opt)}
- predict_dataframe(df, text_col='texte_nettoye', pipeline_path=..., train_if_missing=False, data_paths=None) -> df with 'prediction_ml'
- optionally update_mongo_predictions(df, mongo_uri, db_name, collection_name)
"""

import re
import os
from typing import List, Optional, Union, Dict, Any

import unidecode
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
import joblib

# -------------------------
# Nettoyage du texte (repris du notebook)
# -------------------------
def clean_text(txt: Optional[str]) -> str:
    """
    Nettoie une chaîne de caractères :
    - supprime balises HTML et URLs
    - enlève accents (unidecode)
    - garde alphanumériques + espaces
    - met en minuscules et normalise les espaces
    """
    if pd.isna(txt) or txt is None:
        return ""
    s = str(txt)
    s = re.sub(r"<[^>]+>", " ", s)                    # Supprime les balises HTML
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)     # Supprime les URLs
    s = unidecode.unidecode(s)                       # Supprime les accents
    s = re.sub(r"[^a-zA-Z0-9\s]", " ", s)            # Garder seulement alphanumérique
    s = s.lower()                                    # Mettre en minuscules
    s = " ".join(s.split())                          # Normaliser les espaces
    return s

# -------------------------
# Construction du pipeline (TF-IDF + LogisticRegression)
# -------------------------
def build_pipeline() -> Pipeline:
    """
    Construit et retourne le pipeline TF-IDF + LogisticRegression
    (mêmes paramètres que dans le notebook).
    """
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=500, random_state=42))
    ])
    return pipe

# -------------------------
# Sauvegarde / Chargement
# -------------------------
def save_pipeline(pipe: Pipeline, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    joblib.dump(pipe, path)
    return path

def load_pipeline(path: str) -> Optional[Pipeline]:
    if path and os.path.exists(path):
        return joblib.load(path)
    return None

# -------------------------
# Chargement de données locales (si nécessaire pour entraînement)
# Cherche dans data/ les fichiers usuels vus dans ton repo
# -------------------------
def load_local_dataset(data_paths: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
    """
    Tente de charger un DataFrame utilitaire à partir de fichiers locaux
    (par défaut regarde dans data/avis_derive.csv, data/avis.json, data/avis_clean.json, data/avis.json).
    Retourne None si aucun fichier trouvé.
    """
    if data_paths is None:
        data_paths = [
            "data/avis_derive.csv",
            "data/avis_clean.json",
            "data/avis.json",
            "data/avis_sample.json",
            "data/avis_derive.json",
        ]
    for p in data_paths:
        if os.path.exists(p):
            try:
                if p.lower().endswith(".csv"):
                    df = pd.read_csv(p)
                else:
                    # JSON peut être orienté records ou non
                    try:
                        df = pd.read_json(p)
                    except ValueError:
                        df = pd.read_json(p, lines=True)
                # normalize column names
                df.columns = [unidecode.unidecode(c).lower().replace(" ", "_") for c in df.columns]
                return df
            except Exception:
                # ignorer et continuer
                continue
    return None

# -------------------------
# Entraînement
# -------------------------
def train_pipeline(
    X: Union[pd.Series, List[str]],
    y: Union[pd.Series, List[int]],
    save_path: str = "data/sentiment_pipeline.joblib",
    save: bool = True,
    test_size: float = 0.2,
    random_state: int = 42,
    return_metrics: bool = False
) -> Union[Pipeline, Dict[str, Any]]:
    """
    Entraîne le pipeline sur X, y. Sauvegarde si save=True.
    X can be a Series or list of raw texts (will be cleaned if need).
    y are integer labels (1..5).
    Si return_metrics True, renvoie un dict contenant pipeline + métriques simples.
    """
    Xs = pd.Series(X).astype(str).apply(clean_text)
    ys = pd.Series(y).astype(int)

    pipe = build_pipeline()
    pipe.fit(Xs, ys)

    if save:
        save_pipeline(pipe, save_path)

    if return_metrics:
        # small eval on train/test split
        X_train, X_test, y_train, y_test = train_test_split(Xs, ys, test_size=test_size, stratify=ys, random_state=random_state)
        pipe2 = build_pipeline()
        pipe2.fit(X_train, y_train)
        y_pred = pipe2.predict(X_test)
        from sklearn.metrics import classification_report, f1_score
        report = classification_report(y_test, y_pred, output_dict=True)
        f1_macro = f1_score(y_test, y_pred, average="macro")
        return {"pipeline": pipe, "report": report, "f1_macro": f1_macro}
    return pipe

# -------------------------
# Prédiction
# -------------------------
def predict(
    texts: Union[str, List[str], pd.Series],
    pipeline_path: str = "data/sentiment_pipeline.joblib",
    train_if_missing: bool = False,
    data_paths: Optional[List[str]] = None,
    return_proba: bool = False
) -> Dict[str, Any]:
    """
    Prédit les étiquettes pour `texts`. 
    - texts peut être une seule chaîne ou une liste/Series.
    - Si le pipeline enregistré est introuvable et train_if_missing=True, tente de charger un dataset local
      et d'entraîner le modèle automatiquement.
    Retourne dict: {'predictions': [...], 'proba': [...] (si demandé and available), 'pipeline_path': path}
    """
    single = False
    if isinstance(texts, str):
        texts = [texts]
        single = True
    texts_series = pd.Series(texts).astype(str).apply(clean_text)

    pipe = load_pipeline(pipeline_path)
    if pipe is None:
        if train_if_missing:
            df = load_local_dataset(data_paths)
            if df is None:
                raise FileNotFoundError("pipeline missing and no local dataset found to train automatically.")
            # try to detect text & label columns
            # prefer colonne 'texte_nettoye' or 'texte' and 'etiquette' for labels
            if "texte_nettoye" in df.columns:
                X_all = df["texte_nettoye"].astype(str)
            elif "texte" in df.columns:
                X_all = df["texte"].astype(str).apply(clean_text)
            else:
                # try common names
                possible_text_cols = [c for c in df.columns if "texte" in c or "text" in c or "contenu" in c or "titre" in c]
                if possible_text_cols:
                    X_all = df[possible_text_cols[0]].astype(str).apply(clean_text)
                else:
                    raise ValueError("Aucun champ texte trouvé dans le dataset local.")
            if "etiquette" in df.columns:
                y_all = df["etiquette"]
            else:
                # try numeric star columns
                possible_label_cols = [c for c in df.columns if c in ("stars", "note", "rating", "etoiles") or "etiquette" in c]
                if possible_label_cols:
                    y_all = df[possible_label_cols[0]]
                else:
                    raise ValueError("Aucun champ étiquette/label trouvé dans le dataset local.")
            pipe = train_pipeline(X_all, y_all, save_path=pipeline_path, save=True)
        else:
            raise FileNotFoundError(f"Pipeline non trouvé à {pipeline_path}. Set train_if_missing=True to auto-train from local data.")

    preds = pipe.predict(texts_series)
    result = {"predictions": preds.tolist(), "pipeline_path": pipeline_path}
    if return_proba and hasattr(pipe, "predict_proba"):
        try:
            proba = pipe.predict_proba(texts_series)
            result["proba"] = proba.tolist()
        except Exception:
            result["proba"] = None
    if single:
        # simplify for single input
        result["predictions"] = result["predictions"][0]
        if "proba" in result and result["proba"] is not None:
            result["proba"] = result["proba"][0]
    return result

# -------------------------
# Helpers pour DataFrame -> ajoute colonne 'prediction_ml'
# -------------------------
def predict_dataframe(
    df: pd.DataFrame,
    text_col: str = "texte_nettoye",
    pipeline_path: str = "data/sentiment_pipeline.joblib",
    train_if_missing: bool = False,
    data_paths: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Prend un DataFrame, effectue le nettoyage si nécessaire et ajoute la colonne 'prediction_ml'
    (int).
    """
    df2 = df.copy()
    if text_col not in df2.columns:
        # attempt to build texte_nettoye from possible columns
        if "texte" in df2.columns:
            df2["texte_nettoye"] = df2["texte"].astype(str).apply(clean_text)
        else:
            # fallback: try first textual column
            txt_cols = [c for c in df2.columns if df2[c].dtype == "object"]
            if txt_cols:
                df2["texte_nettoye"] = df2[txt_cols[0]].astype(str).apply(clean_text)
            else:
                df2["texte_nettoye"] = ""
        text_col = "texte_nettoye"
    texts = df2[text_col].astype(str).tolist()
    res = predict(texts, pipeline_path=pipeline_path, train_if_missing=train_if_missing, data_paths=data_paths)
    preds = res["predictions"]
    df2["prediction_ml"] = preds if isinstance(preds, list) else [preds]
    return df2

# -------------------------
# (Optionnel) Mise à jour MongoDB - repris du notebook
# -------------------------
def update_mongo_predictions(
    df: pd.DataFrame,
    mongo_uri: str = "mongodb://localhost:27017/?authSource=admin",
    db_name: str = "satisfaction",
    collection_name: str = "avis",
    id_col: str = "_id"
):
    """
    Met à jour la collection MongoDB avec la colonne 'prediction_ml' du DataFrame.
    Le DataFrame doit contenir la colonne id_col et prediction_ml.
    """
    from pymongo import MongoClient
    from bson import ObjectId

    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection_name]

    for _, row in df.iterrows():
        _id = row.get(id_col)
        if _id is None:
            continue
        try:
            oid = ObjectId(_id) if not isinstance(_id, ObjectId) else _id
        except Exception:
            oid = _id  # leave as-is if not an ObjectId
        col.update_one({"_id": oid}, {"$set": {"prediction_ml": int(row["prediction_ml"])}})
    client.close()

# -------------------------
# Petit test / utilitaire si lancé seul
# -------------------------
if __name__ == "__main__":
    # test rapide
    print("Vérification: modèle existant ? ->", os.path.exists("data/sentiment_pipeline.joblib"))
    # Si absent, tente d'entraîner sur un dataset local
    try:
        res = predict(["Ceci est un super produit, je suis ravi !", "Très déçu, mauvais service."], train_if_missing=True)
        print("Prédictions:", res)
    except Exception as e:
        print("Erreur (si aucun dataset local disponible) :", str(e))
