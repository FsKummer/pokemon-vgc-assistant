import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def _get_all_poke_urls() -> list:
    """
    Fetches all Pokemon URLs from the API.
    Calls https://pokeapi.co/api/v2/pokemon?limit=1302
    """
    url = "https://pokeapi.co/api/v2/pokemon?limit=1302"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["results"]

def _get_pokemon_info(pokemon_url: str) -> dict:
    """
    Fetches Pokemon info from the API.
    Calls https://pokeapi.co/api/v2/pokemon/{pokemon_id}
    """
    response = requests.get(pokemon_url)
    response.raise_for_status()
    raw_pokemon_info = response.json()
    type_1 = raw_pokemon_info['types'][0]['type']['name']
    type_2 = raw_pokemon_info['types'][1]['type']['name'] if len(raw_pokemon_info['types']) > 1 else None
    base_hp = raw_pokemon_info['stats'][0]['base_stat']
    base_attack = raw_pokemon_info['stats'][1]['base_stat']
    base_defense = raw_pokemon_info['stats'][2]['base_stat']
    base_sp_attack = raw_pokemon_info['stats'][3]['base_stat']
    base_sp_defense = raw_pokemon_info['stats'][4]['base_stat']
    base_speed = raw_pokemon_info['stats'][5]['base_stat']

    pokemon_info = {
        'id': raw_pokemon_info['id'],
        'name': raw_pokemon_info['name'],
        'type_1': type_1,
        'type_2': type_2,
        'base_hp': base_hp,
        'base_attack': base_attack,
        'base_defense': base_defense,
        'base_sp_attack': base_sp_attack,
        'base_sp_defense': base_sp_defense,
        'base_speed': base_speed
    }

    return pokemon_info

def save_pokemon_info_to_csv() -> None:
    """
    Opens a CSV file and appends Pokemon info to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/pokemon_info_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'type_1', 'type_2', 'base_hp', 'base_attack', 'base_defense', 'base_sp_attack', 'base_sp_defense', 'base_speed'])

        pokemon_urls = _get_all_poke_urls()
        for pokemon_url in pokemon_urls:
            pokemon_info = _get_pokemon_info(pokemon_url['url'])
            writer.writerow(pokemon_info.values())

    print(f"Pokemon info saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='pokemon_info')


def __main__():
    save_pokemon_info_to_csv()

if __name__ == "__main__":
    __main__()
