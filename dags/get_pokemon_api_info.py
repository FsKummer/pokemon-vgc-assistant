import os
import pendulum
import sys

# Add the path to the modules to the PYTHONPATH
sys.path.append(f"{os.getenv('AIRFLOW_HOME')}/pokemon_vgc_assistant")

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pokemon_vgc_assistant.extract.pokemon_info.get_all_pokemons import save_pokemon_info_to_csv
from pokemon_vgc_assistant.extract.pokemon_info.get_all_moves import save_move_info_to_csv
from pokemon_vgc_assistant.extract.pokemon_info.get_all_items import save_item_info_to_csv
from pokemon_vgc_assistant.extract.pokemon_info.get_all_abilities import save_ability_info_to_csv
from pokemon_vgc_assistant.extract.pokemon_info.get_types import save_type_info_to_csv

# IMPORT YOUR PACKAGES HERE

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")

with DAG(
    "pokemon_api_info",
    description='A DAG to get and information from Pokemon API',
    start_date=pendulum.yesterday(tz="UTC"),
    catchup=False,
    default_args={"depends_on_past": False}
) as dag:

    get_pokemon =  PythonOperator(
        task_id='get_pokemons',
        python_callable=save_pokemon_info_to_csv,
        dag=dag,
    )

    get_pokemon_moves =  PythonOperator(
        task_id='get_pokemon_moves',
        python_callable=save_move_info_to_csv,
        dag=dag,
    )

    get_items =  PythonOperator(
        task_id='get_items',
        python_callable=save_item_info_to_csv,
        dag=dag,
    )

    get_abilities = PythonOperator(
        task_id='get_abilities',
        python_callable=save_ability_info_to_csv,
        dag=dag,
    )

    get_types = PythonOperator(
        task_id='get_types',
        python_callable=save_type_info_to_csv,
        dag=dag,
    )

    trigger_load_dag = TriggerDagRunOperator(
        task_id='trigger_load_dag',
        trigger_dag_id='load_pokemon_data_to_bigquery',
        dag=dag,
    )

    get_pokemon >> get_pokemon_moves >> get_items >> get_abilities >> get_types >> trigger_load_dag
