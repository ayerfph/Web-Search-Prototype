from collections.abc import Sequence
from typing import Any

import psycopg

from .validate import validate_pokemon


DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "pokemon",
    "user": "postgres",
    "password": "postgres",
}


PokemonData = dict[str, dict[str, Any]]


def _load_single_pokemon(
    connection: psycopg.Connection,
    data: PokemonData,
) -> None:
    """
    Insert or update one Pokémon across all database tables.

    This function assumes the data has already been validated.
    """

    connection.execute(
        """
        INSERT INTO pokemon (
            id,
            name,
            height,
            weight
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight
        """,
        (
            data["pokemon"]["id"],
            data["pokemon"]["name"],
            data["pokemon"]["height"],
            data["pokemon"]["weight"],
        ),
    )

    connection.execute(
        """
        INSERT INTO pokemon_types (
            id,
            type_1,
            type_2
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            type_1 = EXCLUDED.type_1,
            type_2 = EXCLUDED.type_2
        """,
        (
            data["pokemon_types"]["id"],
            data["pokemon_types"]["type_1"],
            data["pokemon_types"]["type_2"],
        ),
    )

    connection.execute(
        """
        INSERT INTO pokemon_abilities (
            id,
            ability_name
        )
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET
            ability_name = EXCLUDED.ability_name
        """,
        (
            data["pokemon_abilities"]["id"],
            data["pokemon_abilities"]["ability_name"],
        ),
    )

    connection.execute(
        """
        INSERT INTO pokemon_stats (
            id,
            hp,
            attack,
            defense,
            special_attack,
            special_defense,
            speed
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            hp = EXCLUDED.hp,
            attack = EXCLUDED.attack,
            defense = EXCLUDED.defense,
            special_attack = EXCLUDED.special_attack,
            special_defense = EXCLUDED.special_defense,
            speed = EXCLUDED.speed
        """,
        (
            data["pokemon_stats"]["id"],
            data["pokemon_stats"]["hp"],
            data["pokemon_stats"]["attack"],
            data["pokemon_stats"]["defense"],
            data["pokemon_stats"]["special_attack"],
            data["pokemon_stats"]["special_defense"],
            data["pokemon_stats"]["speed"],
        ),
    )


def load_pokemon_data(data: PokemonData) -> None:
    """
    Load one validated Pokémon into PostgreSQL.
    """

    validate_pokemon(data)

    with psycopg.connect(**DB_CONFIG) as connection:
        _load_single_pokemon(connection, data)


def load_pokemon_data_batch(
    pokemon_records: Sequence[PokemonData],
) -> None:
    """
    Load multiple validated Pokémon into PostgreSQL.

    All records are loaded using one database connection and one
    transaction. If one record fails, the transaction is rolled back.
    """

    if not pokemon_records:
        raise ValueError("Cannot load an empty Pokémon collection")

    for record in pokemon_records:
        validate_pokemon(record)

    with psycopg.connect(**DB_CONFIG) as connection:
        for record in pokemon_records:
            _load_single_pokemon(connection, record)


def run_pipeline(name: str) -> None:
    """
    Run the complete pipeline for one Pokémon.

    This preserves the original single-Pokémon usage.
    """

    from .extract import fetch_data
    from .transform import transform_pokemon

    extracted_data = fetch_data(name)

    print("\n===== EXTRACTED DATA =====")
    print(extracted_data)

    transformed_data = transform_pokemon(extracted_data)

    print("\n===== TRANSFORMED DATA =====")
    print(transformed_data)

    validate_pokemon(transformed_data)

    print("\n===== VALIDATION PASSED =====")

    load_pokemon_data(transformed_data)

    print("\n===== LOAD COMPLETE =====")
    print(f"Successfully loaded {name} into PostgreSQL.")


if __name__ == "__main__":
    run_pipeline("mew")