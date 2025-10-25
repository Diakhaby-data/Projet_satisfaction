# satisfaction_dag.py
# DAG Airflow pour le pipeline de traitement des avis clients
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
import json
import os
import pandas as pd
import logging

# Arguments par défaut du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Config des fichiers
DATA_DIR = "/opt/airflow/data"
RAW_FILE = os.path.join(DATA_DIR, "avis.json")
CLEAN_FILE = os.path.join(DATA_DIR, "avis_clean.json")
SUMMARY_FILE = os.path.join(DATA_DIR, "avis_summary.json")
REPORT_FILE = os.path.join(DATA_DIR, "satisfaction_report.txt")

# Fonctions Python pour les tâches de nettoyage et d'agrégation
def clean_data():
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    cleaned = [avis for avis in data if avis.get("contenu")]
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False)
    logging.info(f"{len(cleaned)} avis nettoyés")

def aggregate_data():
    df = pd.read_json(CLEAN_FILE)
    summary = df.groupby("nombre_etoile").size().to_dict()
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False)
    logging.info(f"Agrégation terminée : {summary}")

def load_data_to_mongo():
    try:
        client = MongoClient("mongodb://dkb:diakhaby@mongo_service:27017/")
        db = client["satisfaction"]
        collection = db["avis"]

        with open(CLEAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            result = collection.insert_many(data)
            logging.info(f"{len(result.inserted_ids)} avis insérés dans MongoDB")
        elif isinstance(data, dict):
            result = collection.insert_one(data)
            logging.info(f"1 avis inséré : {result.inserted_id}")
        else:
            logging.warning("Aucun avis à insérer")

    except Exception as e:
        logging.error(f"Erreur MongoDB : {e}")
        raise

def generate_report():
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=== Rapport de satisfaction ===\n")
        f.write(f"Date : {datetime.now()}\n\n")
        if os.path.exists(SUMMARY_FILE):
            with open(SUMMARY_FILE, "r", encoding="utf-8") as summary_f:
                summary = json.load(summary_f)
            for etoile, count in summary.items():
                f.write(f"{etoile} étoiles : {count} avis\n")
    logging.info(f"Rapport créé : {REPORT_FILE}")

# Définition du DAG et des tâches 
with DAG(
    dag_id="satisfaction_pipeline",
    default_args=default_args,
    description="Pipeline complet de traitement des avis clients",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["satisfaction"],
) as dag:

    scrape_data = BashOperator(
        task_id="scrape_data",
        bash_command="python /opt/airflow/scripts/scrape_data.py",
    )

    clean_data_op = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
    )

    aggregate_data_op = PythonOperator(
        task_id="aggregate_data",
        python_callable=aggregate_data,
    )

    load_to_mongo = PythonOperator(
        task_id="load_to_mongo",
        python_callable=load_data_to_mongo,
    )

    # Appelle du script ML externe
    predict_sentiment_op = BashOperator(
        task_id="predict_sentiment",
        bash_command="python /opt/airflow/app/run_predictions.py",
    )

    generate_report_op = PythonOperator(
        task_id="generate_report",
        python_callable=generate_report,
    )

    notify_team = BashOperator(
        task_id="notify_team",
        bash_command='echo "Pipeline terminé !"',
    )

    # Ordonnancement des tâches 
    scrape_data >> clean_data_op >> aggregate_data_op >> load_to_mongo
    load_to_mongo >> [generate_report_op, predict_sentiment_op] >> notify_team
