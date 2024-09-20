import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def _get_battle_ids(format_id: str, before: int = None, until_id: str = None, csv_writer=None) -> None:
    """
    Fetch battle IDs from Pokemon Showdown's API and save them to CSV after each request.
    Calls https://replay.pokemonshowdown.com/search.json?format={format_id}&before=<before>
    """
    base_url = f"https://replay.pokemonshowdown.com/search.json?format={format_id}"

    while True:
        if before:
            url = f"{base_url}&before={before}"
        else:
            url = base_url

        print(f"Fetching battles before {before}, continuing...")
        response = requests.get(url)
        response.raise_for_status()

        battle_search = response.json()

        if csv_writer:
            for battle in battle_search:
                if until_id and battle["id"] == until_id:
                    break
                csv_writer.writerow([battle["id"]])

        if len(battle_search) < 51:
            break

        before = battle_search[-1]["uploadtime"]

def save_battle_ids_to_csv(format_id: str ,before: int = None, until_id: str = None) -> None:
    """
    Opens a CSV file and appends battle IDs to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/battle_ids_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['battle_id'])

        _get_battle_ids(format_id=format_id, csv_writer=writer, before=before)

    print(f"Battle IDs saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='battle_ids')

def __main__():
    save_battle_ids_to_csv(format_id='gen9vgc2024regh', before=1723397210)

if __name__ == "__main__":
    __main__()
