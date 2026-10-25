from collections.abc import Mapping
from typing import Any


def validate_pokemon(data: Mapping[str, Any]) -> None:
    """
    Validate transformed Pokémon data.

    Raises:
        ValueError: If the transformed data is invalid.
    """

    required_sections = {
        "pokemon": {"id", "name", "height", "weight"},
        "pokemon_descriptions": {"id", "description", "category"},
        "pokemon_types": {"id", "type_1", "type_2"},
        "pokemon_abilities": {"id", "ability_name"},
        "pokemon_stats": {
            "id",
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
        },
    }

    # Validate sections and required fields
    for section_name, required_fields in required_sections.items():
        if section_name not in data:
            raise ValueError(
                f"Missing required section: {section_name}"
            )

        section = data[section_name]

        if not isinstance(section, Mapping):
            raise ValueError(
                f"Section '{section_name}' must be a dictionary"
            )

        missing_fields = required_fields - set(section.keys())

        if missing_fields:
            raise ValueError(
                f"Section '{section_name}' is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

    pokemon = data["pokemon"]
    pokemon_descriptions = data["pokemon_descriptions"]
    pokemon_types = data["pokemon_types"]
    pokemon_abilities = data["pokemon_abilities"]
    pokemon_stats = data["pokemon_stats"]

    # Validate Pokémon ID
    pokemon_id = pokemon["id"]

    if not isinstance(pokemon_id, int) or isinstance(pokemon_id, bool):
        raise ValueError("'pokemon.id' must be an integer")

    if pokemon_id <= 0:
        raise ValueError("'pokemon.id' must be greater than zero")

    # Validate Pokémon name
    if not isinstance(pokemon["name"], str):
        raise ValueError("'pokemon.name' must be a string")

    if not pokemon["name"].strip():
        raise ValueError("'pokemon.name' cannot be empty")

    # Validate height and weight
    for field_name in ("height", "weight"):
        value = pokemon[field_name]

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"'pokemon.{field_name}' must be an integer"
            )

        if value <= 0:
            raise ValueError(
                f"'pokemon.{field_name}' must be greater than zero"
            )

    # Validate related table IDs
    related_sections = {
        "pokemon_descriptions": pokemon_descriptions,
        "pokemon_types": pokemon_types,
        "pokemon_abilities": pokemon_abilities,
        "pokemon_stats": pokemon_stats,
    }

    for section_name, section in related_sections.items():
        if section["id"] != pokemon_id:
            raise ValueError(
                f"'{section_name}.id' does not match 'pokemon.id'"
            )

    description = pokemon_descriptions["description"]

    if not isinstance(description, str):
        raise ValueError(
            "'pokemon_descriptions.description' must be a string"
        )

    if not description.strip():
        raise ValueError(
            "'pokemon_descriptions.description' cannot be empty"
        )

    # Validate primary type
    type_1 = pokemon_types["type_1"]

    if not isinstance(type_1, str):
        raise ValueError(
            "'pokemon_types.type_1' must be a string"
        )

    if not type_1.strip():
        raise ValueError(
            "'pokemon_types.type_1' cannot be empty"
        )

    # Validate secondary type
    type_2 = pokemon_types["type_2"]

    if type_2 is not None and not isinstance(type_2, str):
        raise ValueError(
            "'pokemon_types.type_2' must be a string or None"
        )

    if type_2 is not None and type_1 == type_2:
        raise ValueError(
            "Primary and secondary types cannot be the same"
        )

    # Validate ability
    ability_name = pokemon_abilities["ability_name"]

    if not isinstance(ability_name, str):
        raise ValueError(
            "'pokemon_abilities.ability_name' must be a string"
        )

    if not ability_name.strip():
        raise ValueError(
            "'pokemon_abilities.ability_name' cannot be empty"
        )

    # Validate stats
    stat_fields = (
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
    )

    for field_name in stat_fields:
        value = pokemon_stats[field_name]

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"'pokemon_stats.{field_name}' must be an integer"
            )

        if value < 0:
            raise ValueError(
                f"'pokemon_stats.{field_name}' cannot be negative"
            )