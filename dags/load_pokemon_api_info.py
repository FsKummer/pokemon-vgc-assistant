from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
import os
from datetime import datetime

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
    "load_pokemon_data_to_bigquery",
    description='A DAG to load Pokémon data from GCS to BigQuery',
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:

    load_pokemon_data = BigQueryInsertJobOperator(
        task_id='load_pokemon_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/pokemon_info/{year}/{month}/{day}/pokemon_info_{date_today.strftime('%Y_%m_%d')}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "pokemons",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    load_moves_data = BigQueryInsertJobOperator(
        task_id='load_moves_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/move_info/{year}/{month}/{day}/move_info_{date_today.strftime('%Y_%m_%d')}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "moves",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    load_items_data = BigQueryInsertJobOperator(
        task_id='load_items_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/item_info/{year}/{month}/{day}/item_info_{date_today.strftime('%Y_%m_%d')}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "items",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    load_abilities_data = BigQueryInsertJobOperator(
        task_id='load_abilities_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/ability_info/{year}/{month}/{day}/ability_info_{date_today.strftime('%Y_%m_%d')}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "abilities",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    load_types_data = BigQueryInsertJobOperator(
        task_id='load_types_data_to_bq',
        configuration={
            "load": {
                "sourceUris": [f"gs://{LAKE_BUCKET}/type_info/{year}/{month}/{day}/type_info_{date_today.strftime('%Y_%m_%d')}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BRONZE_DATASET_NAME,
                    "tableId": "types",
                },
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_TRUNCATE",
                "autodetect": True
            }
        }
    )

    load_pokemon_data >> load_moves_data >> load_items_data >> load_abilities_data >> load_types_data
