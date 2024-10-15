import requests
import csv
from pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
from pokemon_vgc_assistant.extract.battle_info.get_battle_info import _get_battle_info
import base64

def process_battle_ids(input_csv: str, output_csv: str) -> None:
    """
    Opens a CSV file containing battle IDs, fetches battle info using the API,
    and writes the battle information to another CSV.
    """
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        writer.writerow(['battle_id', 'format_id', 'log', 'upload_time'])

        next(reader)

        for row in reader:
            battle_id = row[0]
            try:
                print(f"Fetching battle info for battle_id: {battle_id}")
                battle_info = _get_battle_info(battle_id)
                format_id = battle_info['formatid']
                log = battle_info['log']
                encoded_log = base64.b64encode(log.encode('utf-8')).decode('utf-8')
                upload_time = battle_info['uploadtime']
                writer.writerow([battle_id, format_id, encoded_log, upload_time])
            except requests.RequestException as e:
                print(f"Failed to fetch battle {battle_id}: {e}")

def __main__():
    input_csv = 'data/battle_ids_2024_09_25.csv'
    output_csv = 'data/battle_info_2024_09_25.csv'
    process_battle_ids(input_csv, output_csv)
    upload_file_to_lake(output_csv, 'battle_info')

if __name__ == "__main__":
    __main__()
