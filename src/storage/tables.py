import pandas as pd
import os

def create_tables():
    """Lit le CSV des sociétés et retourne le DataFrame"""
    csv_path = os.path.join("data", "raw", "societes.csv")
    df = pd.read_csv(csv_path)
    print("Nombre de sociétés :", len(df))
    print("Noms :", df["nom"].tolist())
    return df

