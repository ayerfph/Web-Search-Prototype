from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterable
from typing import Any

import requests


API_BASE_URL = "https://pokeapi.co/api/v2"
GENERATION_1_ID = 1

# Shorter bounded timeout prevents long hangs.
REQUEST_TIMEOUT_SECONDS = 15

# Bounded concurrency avoids overwhelming the device or API.
MAX_API_WORKERS = 8


def _get_json(url: str, description: str) -> dict[str, Any]:
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

    except requests.Timeout as error:
        raise RuntimeError(
            f"{description} request timed out"
        ) from error

    except requests.RequestException as error:
        status_code = getattr(
            getattr(error, "response", None),
            "status_code",
            "unknown",
        )

        raise RuntimeError(
            f"{description} request failed with status {status_code}"
        ) from error

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError(
            f"{description} returned an invalid response"
        )

    return payload


def fetch_data(identifier: int | str) -> dict[str, Any]:
    """Fetch one Pokémon from PokéAPI by ID or name."""

    normalized_identifier = str(identifier).strip().lower()

    if not normalized_identifier:
        raise ValueError(
            "Pokémon identifier cannot be empty"
        )

    url = (
        f"{API_BASE_URL}/pokemon/"
        f"{normalized_identifier}"
    )

    return _get_json(
        url,
        f"Pokémon '{normalized_identifier}'",
    )


def _extract_species_name(entry: object) -> str:
    if not isinstance(entry, dict):
        raise ValueError(
            "PokéAPI returned an invalid Generation 1 species entry"
        )

    name = entry.get("name")

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "PokéAPI returned a species entry without a valid name"
        )

    return name


def fetch_generation_1() -> list[dict[str, Any]]:
    """
    Fetch all Generation 1 Pokémon with bounded parallel requests.

    The API metadata request is performed once. Detailed Pokémon requests
    are then fetched concurrently with a fixed worker limit.
    """

    generation_url = (
        f"{API_BASE_URL}/generation/{GENERATION_1_ID}"
    )

    generation_data = _get_json(
        generation_url,
        "PokéAPI Generation 1",
    )

    species = generation_data.get("pokemon_species", [])

    if (
        not isinstance(species, Iterable)
        or isinstance(species, (str, bytes))
        or not species
    ):
        raise ValueError(
            "PokéAPI returned no Generation 1 Pokémon"
        )

    names = [
        _extract_species_name(entry)
        for entry in species
    ]

    worker_count = min(MAX_API_WORKERS, len(names))

    with ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="pokeapi",
    ) as executor:
        pokemon_data = list(
            executor.map(fetch_data, names)
        )

    return sorted(
        pokemon_data,
        key=lambda pokemon: pokemon["id"],
    )