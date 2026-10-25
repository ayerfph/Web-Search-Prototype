from typing import Any


def transform_pokemon(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Transform a PokéAPI Pokémon response into database-ready rows.

    Args:
        data: Raw Pokémon data returned by PokéAPI.

    Returns:
        Dictionary containing rows for the Pokémon,
        types, abilities, and stats tables.
    """

    stats = {
        stat["stat"]["name"]: stat["base_stat"]
        for stat in data.get("stats", [])
    }

    types = [
        pokemon_type["type"]["name"]
        for pokemon_type in data.get("types", [])
    ]

    abilities = [
        ability["ability"]["name"]
        for ability in data.get("abilities", [])
    ]

    pokemon_id = data["id"]

    return {
        "pokemon": {
            "id": pokemon_id,
            "name": data["name"],
            "height": data.get("height"),
            "weight": data.get("weight"),
        },

        "pokemon_types": {
            "id": pokemon_id,
            "type_1": types[0] if len(types) > 0 else None,
            "type_2": types[1] if len(types) > 1 else None,
        },

        "pokemon_abilities": {
            "id": pokemon_id,
            "ability_name": ", ".join(abilities) if abilities else None,
        },

        "pokemon_stats": {
            "id": pokemon_id,
            "hp": stats.get("hp"),
            "attack": stats.get("attack"),
            "defense": stats.get("defense"),
            "special_attack": stats.get("special-attack"),
            "special_defense": stats.get("special-defense"),
            "speed": stats.get("speed"),
        },
    }