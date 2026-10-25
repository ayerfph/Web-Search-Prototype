import psycopg

from .extract import fetch_data
from .transform import transform_pokemon
from .validate import validate_pokemon


DB_CONFIG = {
    "host": "postgres", #change it into localhost if needed
    "port": 5432,
    "dbname": "pokemon",
    "user": "postgres",
    "password": "postgres",
}


def load_pokemon_data(data: dict) -> None:
    """
    Load transformed Pokémon data into PostgreSQL.

    Args:
        data: Transformed Pokémon data containing
            pokemon, types, abilities, and stats.
    """

    with psycopg.connect(**DB_CONFIG) as conn:

        # ---------------------------------------------------------
        # 1. Load Pokemon
        # ---------------------------------------------------------
        conn.execute(
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

        # ---------------------------------------------------------
        # 2. Load Pokemon Types
        # ---------------------------------------------------------
        conn.execute(
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

        # ---------------------------------------------------------
        # 3. Load Pokemon Abilities
        # ---------------------------------------------------------
        conn.execute(
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

        # ---------------------------------------------------------
        # 4. Load Pokemon Stats
        # ---------------------------------------------------------
        conn.execute(
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


def run_pipeline(name: str) -> None:
    """Run the complete Pokémon ETL pipeline."""

    # EXTRACT
    extracted_data = fetch_data(name)

    print("\n===== EXTRACTED DATA =====")
    print(extracted_data)

    # TRANSFORM
    transformed_data = transform_pokemon(extracted_data)

    print("\n===== TRANSFORMED DATA =====")
    print(transformed_data)

    # VALIDATE
    validate_pokemon(transformed_data)

    print("\n===== VALIDATION PASSED =====")

    # LOAD
    load_pokemon_data(transformed_data)

    print("\n===== LOAD COMPLETE =====")
    print(f"Successfully loaded {name} into PostgreSQL.")


if __name__ == "__main__":
    run_pipeline("mew")