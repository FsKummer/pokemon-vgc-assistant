import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def get_all_types() -> list:
    """
    Fetches all type effectiveness from the API.
    Calls https://pokeapi.co/api/v2/type?limit=100
    """
    url = "https://pokeapi.co/api/v2/type?limit=100"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["results"]

def get_type_info(type_url: str) -> dict:
    """
    Fetches type info from the API.
    Calls https://pokeapi.co/api/v2/type/{type_id}
    """
    print(f"Fetching type info from {type_url}")
    response = requests.get(type_url)
    response.raise_for_status()
    raw_type_info = response.json()
    damage_relations = raw_type_info.get('damage_relations', {})

    type_info = {
        'id': raw_type_info['id'],
        'name': raw_type_info['name'],
        'damage_relations': damage_relations
    }

    return type_info

def save_type_info_to_csv() -> None:
    """
    Opens a CSV file and appends type info to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/type_info_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'damage_relations'])

        type_urls = get_all_types()

        for type_url in type_urls:
            type_info = get_type_info(type_url['url'])
            writer.writerow([type_info['id'], type_info['name'], type_info['damage_relations']])

    print(f"Type info saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='type_info')

def __main__():
    save_type_info_to_csv()

if __name__ == "__main__":
    __main__()
