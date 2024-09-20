import requests


def _get_battle_info(battle_id: str) -> dict:
    """
    Calls https://replay.pokemonshowdown.com/<battle_id>.json
    and returns the json with the battle info and logs.
    """
    url = f"https://replay.pokemonshowdown.com/{battle_id}.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    battle_info = response.json()

    if battle_info:
        return battle_info
    else:
        raise ValueError(f"No battle found for ID: {battle_id}")

def __main__():
    battle_info = _get_battle_info('gen9vgc2024regh-2201693665')
    print(battle_info)

if __name__ == "__main__":
    __main__()
