import requests


def get_pokemon(name: str) -> dict:
    """Fetch Pokémon information from PokéAPI.

    Args:
        name: Pokémon name.

    Returns:
        Pokémon data as a dictionary.

    Raises:
        requests.HTTPError: If the API request fails.
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.Timeout as error:
        raise RuntimeError("PokeAPI requests timed out") from error
    
    except requests.HTTPError as error:
        raise RuntimeError(
            f"PokeAPI request failed: {response.status_code}"
        ) from error

    return response.json()


pokemon = get_pokemon("pikachu")
