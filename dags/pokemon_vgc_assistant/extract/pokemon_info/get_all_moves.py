import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def _get_all_moves() -> list:
    """
    Fetches all moves from the API.
    Calls https://pokeapi.co/api/v2/move?limit=937
    """
    url = "https://pokeapi.co/api/v2/move?limit=937"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["results"]

def _get_move_info(move_url: str) -> dict:
    """
    Fetches move info from the API.
    Calls https://pokeapi.co/api/v2/move/{move_id}
    """
    response = requests.get(move_url)
    response.raise_for_status()
    raw_move_info = response.json()
    effect_entries = raw_move_info.get('effect_entries', [])
    move_info = {
        'id': raw_move_info['id'],
        'name': raw_move_info['name'],
        'type': raw_move_info['type']['name'],
        'power': raw_move_info['power'],
        'pp': raw_move_info['pp'],
        'accuracy': raw_move_info['accuracy'],
        'priority': raw_move_info['priority'],
        'target': raw_move_info['target']['name'],
        'damage_class': raw_move_info['damage_class']['name'],
        'effect_chance': raw_move_info['effect_chance'],
        'effect_entries': effect_entries[0].get('short_effect') if effect_entries else None
    }

    return move_info
    """
    Checks if a move is new by comparing its ID with the ones already saved in the CSV file.
    """
    date_today = datetime.now()
    filepath = f"data/move_info_{date_today.strftime('%Y_%m_%d')}.csv"

    try:
        with open(filepath, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if int(row[0]) == int(move_id):
                    return False
    except FileNotFoundError:
        pass

    return True

def save_move_info_to_csv() -> None:
    """
    Opens a CSV file and appends move info to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/move_info_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'type', 'power', 'pp', 'accuracy', 'priority', 'target', 'damage_class', 'effect_chance', 'effect_entries'])

        move_urls = _get_all_moves()
        for move_url in move_urls:
            move_info = _get_move_info(move_url['url'])
            print(f"Fetching move {move_info['name']}...")
            writer.writerow(move_info.values())

    print(f"Move info saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='move_info')

def __main__():
    save_move_info_to_csv()

if __name__ == "__main__":
    __main__()
