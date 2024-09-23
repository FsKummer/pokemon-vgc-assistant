import csv
from dags.pokemon_vgc_assistant.extract.upload_file_to_lake import upload_file_to_lake
import base64

def fix_csv(input_csv: str, output_csv: str) -> None:
    """
    Reads the original CSV, encodes the log field using Base64,
    and saves it back to a new CSV to avoid issues with quotes and newlines.
    """
    with open(input_csv, 'r', newline='', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

        # Write the headers
        headers = next(reader)
        writer.writerow(headers)

        # Process each row
        for row in reader:
            # Assuming the log is in the third column (index 2)
            log = row[2]

            # Encode the log using Base64 to avoid issues with special characters
            encoded_log = base64.b64encode(log.encode('utf-8')).decode('utf-8')

            # Replace the log in the row with the encoded version
            row[2] = encoded_log

            # Write the fixed row to the new CSV
            writer.writerow(row)

    print(f"Fixed CSV saved to {output_csv}")

# Example usage
input_csv = 'data/battle_info_2024_09_17.csv'
output_csv = 'data/battle_info_1.csv'

fix_csv(input_csv, output_csv)
upload_file_to_lake(output_csv, 'battle_info')

input_csv = 'data/battle_info_2024_09_16.csv'
output_csv = 'data/battle_info_2.csv'

fix_csv(input_csv, output_csv)
upload_file_to_lake(output_csv, 'battle_info')
