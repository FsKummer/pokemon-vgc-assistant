import requests
import csv

def _get_battle_ids(format_id: str, before: int = None, after: int = None, csv_writer=None) -> None:
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
                csv_writer.writerow([battle["id"]])

        if len(battle_search) < 51:
            break

        before = battle_search[-1]["uploadtime"]

def save_battle_ids_to_csv(format_id: str ,before: int = None) -> None:
    """
    Opens a CSV file and appends battle IDs to it as they are fetched.
    """
    filepath = '/data/battle_ids.csv'
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['battle_id'])

        # Fetch and save battle IDs recursively
        _get_battle_ids(format_id='gen9vgc2024regh' ,csv_writer=writer)

    print(f"Battle IDs saved to '{filepath}'.")


def __main__():
    save_battle_ids_to_csv()

if __name__ == "__main__":
    __main__()
