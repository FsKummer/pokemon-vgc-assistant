import pandas as pd
import os
import json
import pdb

# Environment Variables
PROJECT_ID = os.environ['PROJECT_ID']
GOLD_DATASET_NAME = os.environ['GOLD_DATA_SET_NAME']
SILVER_DATASET_NAME = os.environ['SILVER_DATA_SET_NAME']


def fetch_data() -> pd.DataFrame:
    chunk_size = 1000
    offset = 0


    # Fetch battle data from BigQuery
    while True:
        sql_query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{SILVER_DATASET_NAME}.battles`
        LIMIT {chunk_size} OFFSET {offset}
        """
        print("Fetching data from BigQuery...")
        battles_chunk = pd.read_gbq(sql_query, project_id=PROJECT_ID)

        if battles_chunk.empty:
            print("No more data to process.")
            return

        # Transform the fetched battles
        transform_battles(battles_chunk)
        offset += chunk_size

def transform_battles(battles: pd.DataFrame) -> None:
    parsed_battle_actions = []
    parsed_battle_compositions = []
    parsed_pokemon_teams = []
    parsed_battles = []

    for _, row in battles.iterrows():
        battle_id = row['battle_id']
        turns = json.loads(row['turns'])
        team_p1 = json.loads(row['team_p1'])
        team_p2 = json.loads(row['team_p2'])
        player_1 = row['player_1']
        player_2 = row['player_2']

        for pokemon in team_p1:
            parsed_pokemon_teams.append({
                "battle_id": battle_id,
                "player": player_1,
                "pokemon": pokemon
            })
        for pokemon in team_p2:
            parsed_pokemon_teams.append({
                "battle_id": battle_id,
                "player": player_2,
                "pokemon": pokemon
            })

        for turn_number, turn_data in turns.items():
            moves = turn_data.get('moves', [])
            battle_field_start = turn_data.get('battle_field_state_start', {})

            # Extract battle actions (from the moves array)
            for action_number, move in enumerate(moves, start=1):
                parsed_battle_actions.append({
                    "battle_id": battle_id,
                    "turn_number": turn_number,
                    "action_number": action_number,
                    "action_name": move.get("action", ""),
                    "move_name": move.get("move", ""),
                    "ability_name": move.get("ability", ""),
                    "actor_name": move.get("actor", ""),
                    "target_name": move.get("target", ""),
                    "player_name": move.get("player", ""),
                    "description": move.get("description", "")
                })

            # Extract team compositions for each turn (before the moves)
            parsed_battle_compositions.append({
                "battle_id": battle_id,
                "turn_number": turn_number ,
                "player": player_1,
                "pokemon_a": battle_field_start.get(player_1, {}).get('a', ""),
                "pokemon_b": battle_field_start.get(player_1, {}).get('b', "")
            })
            parsed_battle_compositions.append({
                "battle_id": battle_id,
                "turn_number": turn_number,
                "player": player_2,
                "pokemon_a": battle_field_start.get(player_2, {}).get('a', ""),
                "pokemon_b": battle_field_start.get(player_2, {}).get('b', "")
            })

        parsed_battles.append({
            "battle_id": battle_id,
            "log": row['log'],
            "player_1": player_1,
            "player_2": player_2,
            "winner": row['winner'],
            "upload_time": row['upload_time'],
            "format_id": row['format_id']
        })

    # Convert lists to DataFrames
    parsed_battles_df = pd.DataFrame(parsed_battles)
    battle_actions_df = pd.DataFrame(parsed_battle_actions)
    battle_compositions_df = pd.DataFrame(parsed_battle_compositions)
    pokemon_teams_df = pd.DataFrame(parsed_pokemon_teams)

    # Load data into BigQuery
    load_to_bigquery(parsed_battles_df, f'{GOLD_DATASET_NAME}.battles')
    load_to_bigquery(battle_actions_df, f'{GOLD_DATASET_NAME}.battle_actions')
    load_to_bigquery(battle_compositions_df, f'{GOLD_DATASET_NAME}.battle_compositions')
    load_to_bigquery(pokemon_teams_df, f'{GOLD_DATASET_NAME}.pokemon_teams')


def load_to_bigquery(df: pd.DataFrame, destination_table: str) -> None:
    """Helper function to load data into BigQuery."""
    if not df.empty:
        df.to_gbq(destination_table=destination_table, project_id=PROJECT_ID, if_exists='append')
        print(f"Data loaded to {destination_table}.")
    else:
        print(f"No data to load into {destination_table}.")


def main():
    fetch_data()
    print("Data transformation and loading complete.")


if __name__ == '__main__':
    main()
