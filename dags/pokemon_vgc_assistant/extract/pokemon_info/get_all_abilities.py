import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def get_all_abilities() -> list:
    """
    Fetches all abilities from the API.
    Calls https://pokeapi.co/api/v2/ability?limit=367
    """
    url = "https://pokeapi.co/api/v2/ability?limit=367"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["results"]

def get_ability_info(ability_url: str) -> dict:
    """
    Fetches ability info from the API.
    Calls https://pokeapi.co/api/v2/ability/{ability_id}
    """
    print(f"Fetching ability info from {ability_url}")
    response = requests.get(ability_url)
    response.raise_for_status()
    raw_ability_info = response.json()
    effect_entries = raw_ability_info.get('effect_entries', [])
    if effect_entries:
        description = effect_entries[1]['short_effect'] if len(effect_entries) > 1 else effect_entries[0]['short_effect']
    else:
        description = ""

    ability_info = {
        'id': raw_ability_info['id'],
        'name': raw_ability_info['name'],
        'description': description
    }

    return ability_info

def save_ability_info_to_csv() -> None:
    """
    Opens a CSV file and appends ability info to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/ability_info_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'description'])

        ability_urls = get_all_abilities()

        for ability_url in ability_urls:
            ability_info = get_ability_info(ability_url['url'])
            writer.writerow([ability_info['id'], ability_info['name'], ability_info['description']])

    print(f"Ability info saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='ability_info')

def __main__():
    save_ability_info_to_csv()

if __name__ == "__main__":
    __main__()
