from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
import os
from datetime import datetime
from pokemon_vgc_assistant.transform.transform_script_silver import perform_silver_transformation
from pokemon_vgc_assistant.transform.transform_script_gold import perform_gold_transformation

PROJECT_ID = os.getenv("PROJECT_ID")
BRONZE_DATASET_NAME = os.getenv("BRONZE_DATA_SET_NAME")
LAKE_BUCKET = os.getenv("LAKE_BUCKET")
date_today = datetime.now()
year = date_today.strftime("%Y")
month = date_today.strftime("%m")
day = date_today.strftime("%d")

default_args = {
    'depends_on_past': False,
    'start_date': days_ago(1),
}

with DAG(
    "load_battle_info_to_bigquery",
    description='A DAG to load battle info data from GCS to BigQuery',
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:

    load_battle_data = BigQueryInsertJobOperator(
        task_id='load_battle_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/battle_info/{year}/{month}/{day}/battle_info_{year}_{month}_{day}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "battles",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    transform_battle_data_to_silver = PythonOperator(
        task_id='transform_battle_data_to_silver',
        python_callable=perform_silver_transformation,
    )

    transform_battle_data_to_gold = PythonOperator(
        task_id='transform_battle_data_to_gold',
        python_callable=perform_gold_transformation,
    )

    load_battle_data >> transform_battle_data_to_silver >> transform_battle_data_to_gold
