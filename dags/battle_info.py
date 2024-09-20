import os
import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator
from pokemon_vgc_assistant.extract.battle_info.get_all_battles_ids import save_battle_ids_to_csv
from pokemon_vgc_assistant.extract.battle_info.get_all_battle_info import process_battle_ids

# IMPORT YOUR PACKAGES HERE

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")

with DAG(
    "pokemon_battles_info",
    description='A DAG to get and save battle logs from Pokemon battles from a specific format.',
    schedule_interval='*0 0 * * *',
    start_date = pendulum.yesterday(tz="UTC"),
    catchup=False,
    default_args={"depends_on_past": False}
) as dag:

    get_battle_ids =  PythonOperator(
        task_id='get_battle_ids',
        python_callable=save_battle_ids_to_csv,
        op_kwargs={'format_id': 'gen9vgc2024regh'},
        dag=dag,
    )

    get_battle_info = PythonOperator(
        task_id='get_battle_info',
        python_callable=process_battle_ids,
        op_kwargs={'input_csv': f'{AIRFLOW_HOME}/data/battle_ids_{pendulum.now().strftime("%Y_%m_%d")}.csv',
                   'output_csv': f'{AIRFLOW_HOME}/data/battle_info_{pendulum.now().strftime("%Y_%m_%d")}.csv'},
        dag=dag,
    )

    get_battle_ids >> get_battle_info
