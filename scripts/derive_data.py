# -*- coding: utf-8 -*-
import json
import pandas as pd
import sys
import os

# Chemins d'entrée et de sortie
input_path = "/opt/airflow/data/avis.json"
output_path = "/opt/airflow/data/avis_derive.csv"

# Vérifier que le fichier existe
if not os.path.exists(input_path):
    print(f"Erreur : le fichier d'entrée '{input_path}' n'existe pas.", file=sys.stderr)
    sys.exit(1)

try:
    # Charger les données JSON
    with open(input_path, "r", encoding="utf-8") as f:
        avis = json.load(f)

    # Conversion en DataFrame
    df = pd.DataFrame(avis)

    # Normaliser les noms de colonnes en minuscules et enlever les espaces
    df.columns = df.columns.str.lower().str.strip()

    # Colonnes attendues
    expected_cols = ["pays", "nombre_etoile"]

    # Vérifier la présence des colonnes
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Colonnes manquantes dans le DataFrame : {missing_cols}")

    # Statistiques : nombre d'avis par pays
    stats = df.groupby("pays")["nombre_etoile"].count().reset_index()
    stats.rename(columns={"nombre_etoile": "nb_avis"}, inplace=True)

    # Sauvegarder en CSV
    stats.to_csv(output_path, index=False, encoding="utf-8")

    print(f"[OK] Statistiques dérivées enregistrées dans '{output_path}'")

except Exception as e:
    print(f"[ERREUR] {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(1)
