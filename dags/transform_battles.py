from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.python import PythonOperator
from dags.pokemon_vgc_assistant.transform.parse_logs import ParseLogs
import pandas as pd
import os

PROJECT_ID = os.environ['PROJECT_ID']
BRONZE_DATASET_NAME = os.environ['BRONZE_DATASET_NAME']
SILVER_DATASET_NAME = os.environ['SILVER_DATASET_NAME']

def fetch_data() -> pd.DataFrame:
    # Fetch data from BigQuery
    sql_query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{BRONZE_DATASET_NAME}.battles`
    """

    battles = pd.read_gbq(sql_query, project_id=PROJECT_ID)

    return battles

def transform_battles(battles: pd.DataFrame) -> None:
    # Parse and transform the logs
    parsed_battles = []

    for _, row in battles.iterrows():
        log = row['battle_log']
        parser = ParseLogs(log)
        parsed_data = parser.parse_log()

        parsed_battles.append({
            'turns': parsed_data['turns'],
            'team_p1': parsed_data['team_p1'],
            'team_p2': parsed_data['team_p2'],
            'player_1': parsed_data['player_1'],
            'player_2': parsed_data['player_2'],
            'winner': parsed_data['winner']
        })

    # Convert to DataFrame
    parsed_battles_df = pd.DataFrame(parsed_battles)

    # Load to BigQuery
    parsed_battles_df.to_gbq(
        destination_table=f'{PROJECT_ID}.{SILVER_DATASET_NAME}.battles',
        project_id=PROJECT_ID,
        if_exists='replace'
    )


default_args = {
    'owner': 'your_name',
    'start_date': datetime(2022, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'transform_battles',
    default_args=default_args,
    description='DAG to transform battles data',
    schedule_interval='@daily',
)

fetch_data_to_df = PythonOperator(
    task_id='fetch_data_to_df',
    python_callable=fetch_data,
    provide_context=True,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_battles,
    op_args=[fetch_data_to_df.output],
    provide_context=True,
    dag=dag,
)

transform_data_task
