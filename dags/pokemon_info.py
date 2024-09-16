import os
import requests
import pendulum
import csv

from airflow import DAG
from airflow.operators.python_operator import PythonOperator



# IMPORT YOUR PACKAGES HERE

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")


def create_file_if_not_exist(quotes_file: str) -> None:
    if not os.path.exists(quotes_file):
        os.makedirs(os.path.dirname(quotes_file), exist_ok=True)

        with open(quotes_file, 'w') as file:
            pass


def _get_battle_info(battle_id: int) -> str:
    """
    Calls https://replay.pokemonshowdown.com/gen9vgc2024regh-<battle_id>.json
    and returns the json with the battle info and logs.
    """
    url = f"https://replay.pokemonshowdown.com/gen9vgc2024regh{battle_id}.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    battle_info = response.json()
    if battle_info:
        return quotes['quote']
    else:
        raise ValueError("No quotes found in the response.")


def _is_quote_new(quotes_file: str, quote: str) -> bool:
    with open(quotes_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and quote in row:
                    return False
    return True


def _save_quote(quotes_file: str, quote: str) -> None:
    """
    Saves the `quote` in the `quotes_file`
    """
    with open(quotes_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([quote])


def get_quote_and_save_if_new(quotes_file: str) -> None:
    """
    Reuses the _get_quote, _is_quote_new and _save_quote
    functions to get a quote and save it, if it is a new quote.
    """
    quote = _get_quote()

    if _is_quote_new(quotes_file, quote):
        _save_quote(quotes_file, quote)


with DAG(
    "pokemon_battles_info",
    description='A DAG to get and save battle logs from Pokemon battles',
    schedule_interval='*0 0 * * *',
    start_date = pendulum.yesterday(tz="UTC"),
    catchup=False,
    default_args={"depends_on_past": False}
) as dag:
    quotes_file = f"{AIRFLOW_HOME}/data/quotes.csv"

    create_file_if_not_exist_task = PythonOperator(
        task_id='create_file_if_not_exist',
        python_callable=create_file_if_not_exist,
        op_kwargs={'quotes_file': quotes_file},
        dag=dag,
    )

    get_quote_and_save_if_new_task =  PythonOperator(
        task_id='get_quote_and_save_if_new',
        python_callable=get_quote_and_save_if_new,
        op_kwargs={'quotes_file': quotes_file},
        dag=dag,
    )

    create_file_if_not_exist_task >> get_quote_and_save_if_new_task
