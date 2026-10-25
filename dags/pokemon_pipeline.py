from datetime import datetime
import logging
from typing import Any

from airflow.decorators import dag, task  # pyright: ignore[reportAttributeAccessIssue]

from src.extract import fetch_data
from src.load import load_pokemon_data_batch
from src.transform import transform_pokemon
from src.validate import validate_pokemon


log = logging.getLogger(__name__)


GENERATION_ONE_IDS = list(range(1, 152))


def log_action(action: str, **details: Any) -> None:
    """
    Write a consistent, searchable log message.
    """

    detail_text = " ".join(
        f"{key}={value!r}" for key, value in details.items()
    )

    log.info("action=%s %s", action, detail_text)


@dag(
    dag_id="pokemon_etl_pipeline",
    description=(
        "Extract, transform, validate, and load all "
        "Generation 1 Pokémon"
    ),
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "pokemon",
        "retries": 2,
    },
    tags=["pokemon", "etl", "generation-1"],
)
def pokemon_etl_pipeline():
    @task
    
    def extract_pokemon(identifier: int) -> dict:
        """
        Extract one Pokémon.

        This task is dynamically mapped over IDs 1 through 151.
        """

        log.info(
            "action=task_started "
            "task=extract_pokemon "
            "pokemon_id=%s",
            identifier,
        )

        try:
            extracted_data = fetch_data(identifier)

            if not extracted_data:
                raise ValueError(
                    f"No data was returned for Pokémon ID: {identifier}"
                )

            log.info(
                "action=extract_completed "
                "task=extract_pokemon "
                "pokemon_id=%s "
                "pokemon_name=%r",
                identifier,
                extracted_data.get("name"),
            )

            return extracted_data

        except Exception:
            log.exception(
                "action=task_failed "
                "task=extract_pokemon "
                "pokemon_id=%s",
                identifier,
            )
            raise

    @task
    def transform_pokemon_data(extracted_data: dict) -> dict:
        """
        Transform one extracted Pokémon.
        """

        log_action(
            "task_started",
            task="transform_pokemon_data",
        )

        try:
            transformed_data = transform_pokemon(extracted_data)

            if not transformed_data:
                raise ValueError(
                    "Transformation returned empty data"
                )

            log_action(
                "transform_completed",
                pokemon_id=transformed_data["pokemon"]["id"],
                pokemon_name=transformed_data["pokemon"]["name"],
            )

            return transformed_data

        except Exception:
            log.exception(
                "action=task_failed "
                "task=transform_pokemon_data"
            )
            raise

    @task
    def validate_pokemon_data(transformed_data: dict) -> dict:
        """
        Validate one transformed Pokémon.
        """

        log_action(
            "task_started",
            task="validate_pokemon_data",
        )

        try:
            validate_pokemon(transformed_data)

            log_action(
                "validation_passed",
                pokemon_id=transformed_data["pokemon"]["id"],
                pokemon_name=transformed_data["pokemon"]["name"],
            )

            return transformed_data

        except Exception:
            log.exception(
                "action=task_failed "
                "task=validate_pokemon_data"
            )
            raise

    @task
    def load_pokemon_data_to_database(
        validated_records: list[dict],
    ) -> None:
        """
        Load all validated Generation 1 Pokémon in one transaction.
        """

        log.info(
            "action=task_started "
            "task=load_pokemon_data_to_database "
            "record_count=%s",
            len(validated_records),
        )

        try:
            if not validated_records:
                raise ValueError(
                    "No validated Pokémon records were provided"
                )

            load_pokemon_data_batch(validated_records)

            log.info(
                "action=database_load_completed "
                "record_count=%s",
                len(validated_records),
            )

        except Exception:
            log.exception(
                "action=task_failed "
                "task=load_pokemon_data_to_database"
            )
            raise

    extracted_data = extract_pokemon.expand(
        identifier=GENERATION_ONE_IDS
    )

    transformed_data = transform_pokemon_data.expand(
        extracted_data=extracted_data
    )

    validated_data = validate_pokemon_data.expand(
        transformed_data=transformed_data
    )

    load_pokemon_data_to_database(validated_data)


pokemon_etl_pipeline()