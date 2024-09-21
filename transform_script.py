from dags.pokemon_vgc_assistant.transform.parse_logs import ParseLogs
import pandas as pd
import os
from google.cloud import bigquery
import json

# Set up environment variables (alternatively, you can use a config file)
PROJECT_ID = os.environ['PROJECT_ID']
BRONZE_DATASET_NAME = os.environ['BRONZE_DATA_SET_NAME']
SILVER_DATASET_NAME = os.environ['SILVER_DATA_SET_NAME']

# Step 1: Fetch Data from BigQuery
def fetch_data() -> pd.DataFrame:
    # Define your SQL query to fetch the data
    sql_query = f"""
    SELECT
        battle_id,
        CAST(log AS STRING) AS log,
        upload_time,
        format_id
    FROM `{PROJECT_ID}.{BRONZE_DATASET_NAME}.battles`
    """

    # Fetch the data using pandas' read_gbq function
    battles = pd.read_gbq(sql_query, project_id=PROJECT_ID)

    return battles

# Step 2: Transform the fetched data using ParseLogs
def transform_battles(battles: pd.DataFrame) -> None:
    # Parse and transform the logs
    parsed_battles = []

    for _, row in battles.iterrows():
        print(f"Transforming battle with ID: {row['battle_id']}")
        log = str(row['log'])
        parser = ParseLogs(log)
        parsed_data = parser.parse_log()
        turns_json = json.dumps(parsed_data['turns'])
        team_p1_json = json.dumps(parsed_data['team_p1'])
        team_p2_json = json.dumps(parsed_data['team_p2'])
        upload_time = row['upload_time']
        format_id = row['format_id']

        # Add the parsed battle data to the list
        parsed_battles.append({
            'turns': turns_json,
            'team_p1': team_p1_json,
            'team_p2': team_p2_json,
            'player_1': parsed_data['player_1'],
            'player_2': parsed_data['player_2'],
            'winner': parsed_data['winner'],
            upload_time: upload_time,
            format_id: format_id
        })

    # Convert to DataFrame
    parsed_battles_df = pd.DataFrame(parsed_battles)

    # Load the transformed data into BigQuery
    parsed_battles_df.to_gbq(
        destination_table=f'{PROJECT_ID}.{SILVER_DATASET_NAME}.battles',
        project_id=PROJECT_ID,
        if_exists='replace'  # You can change this to 'append' if needed
    )

# Step 3: Main function to run the script
def main():
    print("Fetching data from BigQuery...")
    battles_df = fetch_data()

    print("Transforming battles data...")
    transform_battles(battles_df)

    print("Data transformation and loading complete.")

# Execute the script
if __name__ == '__main__':
    main()
