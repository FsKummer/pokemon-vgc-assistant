import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from datetime import datetime

def get_all_items() -> list:
    """
    Fetches all items from the API.
    Calls https://pokeapi.co/api/v2/item?limit=2180
    """
    url = "https://pokeapi.co/api/v2/item?limit=2180"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()["results"]

def get_item_info(item_url: str) -> dict:
    """
    Fetches item info from the API.
    Calls https://pokeapi.co/api/v2/item/{item_id}
    """
    print(f"Fetching item info from {item_url}")
    response = requests.get(item_url)
    response.raise_for_status()
    raw_item_info = response.json()
    effect_entries = raw_item_info.get('effect_entries', [])
    item_info = {
        'id': raw_item_info['id'],
        'name': raw_item_info['name'],
        'description': effect_entries[0].get('short_effect') if effect_entries else None
    }

    return item_info

def save_item_info_to_csv() -> None:
    """
    Opens a CSV file and appends item info to it as they are fetched.
    """
    date_today = datetime.now()
    filepath = f"data/item_info_{date_today.strftime('%Y_%m_%d')}.csv"

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'description'])

        item_urls = get_all_items()

        for item_url in item_urls:
            item_info = get_item_info(item_url['url'])
            writer.writerow([item_info['id'], item_info['name'], item_info['description']])

    print(f"Item info saved to '{filepath}'.")
    upload_file_to_lake(file_path=filepath, folder_name='item_info')

def __main__():
    save_item_info_to_csv()

if __name__ == "__main__":
    __main__()
