from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 21),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "satisfaction_pipeline",
    default_args=default_args,
    description="Pipeline scraping -> derive -> rapport",
    schedule_interval="@daily",  # exécution chaque jour
    catchup=False,
) as dag:

    # Étape 1 : scraping
    scrape = BashOperator(
        task_id="scrape_data",
        bash_command="python /opt/airflow/scripts/scraper.py"
    )

    # Étape 2 : dérive des données
    derive = BashOperator(
        task_id="derive_data",
        bash_command="python /opt/airflow/scripts/derive_data.py"
    )

    scrape >> derive
