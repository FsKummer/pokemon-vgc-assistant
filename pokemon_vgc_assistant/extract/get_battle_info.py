import requests


def _get_battle_info(battle_id: int) -> str:
    """
    Calls https://replay.pokemonshowdown.com/gen9vgc2024regh-<battle_id>.json
    and returns the json with the battle info and logs.
    """
    url = f"https://replay.pokemonshowdown.com/gen9vgc2024regh-{battle_id}.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    battle_info = response.json()

    if battle_info:
        return battle_info
    else:
        raise ValueError("No battle found.")

def __main__():
    battle_info = _get_battle_info(2201693665)
    print(battle_info)

if __name__ == "__main__":
    __main__()
