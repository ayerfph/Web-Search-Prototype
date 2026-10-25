# Pokémon ETL Pipeline

This project is an Apache Airflow and Astro project that retrieves Generation 1
Pokémon data from [PokéAPI](https://pokeapi.co/), transforms and validates the
responses, loads the results into PostgreSQL, and exports PostgreSQL tables to
CSV files.

The pipeline handles Pokémon IDs 1 through 151 and stores the data in five
related tables:

- `pokemon`: ID, name, height, and weight
- `pokemon_descriptions`: English PokéAPI species summary description and
  category/genus (for example, `Seed Pokémon` for Bulbasaur)
- `pokemon_types`: primary and secondary types
- `pokemon_abilities`: abilities
- `pokemon_stats`: HP, attack, defense, special attack, special defense, and
  speed

## Project layout

```text
pokemon/
├── dags/
│   ├── pokemon_pipeline.py    # Main daily Airflow ETL DAG
│   └── postgres.py            # PostgreSQL connection test DAG
├── src/
│   ├── extract.py             # Requests data from PokéAPI
│   ├── transform.py           # Converts API data into table rows
│   ├── validate.py            # Validates transformed records
│   ├── load.py                # Upserts records into PostgreSQL
│   └── export.py              # Exports tables or query results to CSV
├── src/data/                  # Default local CSV output directory
├── references/
│   └── postgres_setup.txt     # PostgreSQL schema creation SQL
├── tests/                     # Supporting test and API files
├── requirements.txt           # Python dependencies for Astro
├── Dockerfile                 # Astro Runtime image
└── airflow_settings.yaml      # Local Airflow connections and variables
```

## Prerequisites

Install the following before trying the project:

1. **Docker Desktop** or Docker Engine with Compose support.
2. **Visual Studio Code**.
3. The **Astro CLI**.
4. The VS Code extensions:
   - **Docker**
   - **Python**
   - **Astro** (optional, but useful for Astro projects)
   - **Remote - SSH** or **Dev Containers** if the project is on another
     machine or inside a development container

Check the command-line tools:

```bash
docker --version
astro version
```

## Open the project in VS Code

### Project on your local computer

Open a terminal and run:

```bash
cd /path/to/pokemon
code .
```

You can also open VS Code, select **File > Open Folder**, and choose the
project's `pokemon` directory. The folder opened in VS Code should contain
`README.md`, `dags/`, `src/`, and `requirements.txt`.

### Project on a Linux server or VS Code Server

If the project is on a remote Linux machine, install the **Remote - SSH**
extension and:

1. Press `Ctrl+Shift+P` (`Cmd+Shift+P` on macOS).
2. Select **Remote-SSH: Connect to Host...**.
3. Connect to the machine containing the project.
4. Select **File > Open Folder**.
5. Open `/home/pokemon` (or the directory where this project was cloned).

If the project is already open through VS Code Server, open the integrated
terminal with **Terminal > New Terminal** and confirm that the project root is
the current directory:

```bash
pwd
ls
```

The expected project root is `/home/pokemon`. If the terminal is elsewhere:

```bash
cd /home/pokemon
```

### Open the project in a dev container

If a dev-container configuration is added later, use **Dev Containers: Reopen
in Container** from the Command Palette. At present, this repository is
configured primarily for the Astro CLI workflow, so use `astro dev start` from
the project root.

## Start Airflow locally

From the project root, start the Astro development environment:

```bash
astro dev start
```

This starts the local Airflow services in Docker. When startup completes, open:

- Airflow UI: <http://localhost:8080>
- PostgreSQL: `localhost:5432`

The default local Airflow login is normally:

```text
Username: admin
Password: admin
```

If the Astro CLI displays different credentials, use the credentials shown by
the CLI.

Useful commands:

```bash
astro dev status     # Show container status
astro dev logs       # Follow Airflow logs
astro dev bash       # Open a shell in the Astro container
astro dev stop       # Stop the local environment
astro dev restart    # Restart the local environment
```

If port `8080` or `5432` is already in use, stop the process using the port or
configure a different local port in the Astro project settings.

## Configure PostgreSQL

The project expects a PostgreSQL database named `pokemon` with a `postgres`
user. The local database connection values used by the project are:

```text
Host:     localhost       # From the host machine
Port:     5432
Database: pokemon
User:     postgres
Password: postgres
Schema:   public
```

When connecting from inside an Astro/Docker container, the host may be
`postgres` or `host.docker.internal`, depending on where the PostgreSQL
container is running. Use the hostname that resolves in the environment where
the Python command is executed.

To create the database tables, open a shell connected to PostgreSQL and run the
SQL in [references/postgres_setup.txt](./references/postgres_setup.txt).
For example:

```bash
astro dev bash
psql -h postgres -p 5432 -U postgres
```

Then create the database and tables using the SQL in
[references/postgres_setup.txt](./references/postgres_setup.txt). The schema
uses the same `id` as a primary key in all five tables, with foreign keys from
the related tables to `pokemon(id)`. Descriptions are sourced from the English
`flavor_text_entries` in each PokéAPI Pokémon species response.

Re-run the setup script against an existing database after adding this table.
It includes an idempotent migration that adds the missing primary-key
constraint to `pokemon_descriptions`, which is required by the loader's
`ON CONFLICT (id)` upsert.

Verify the tables:

```sql
\c pokemon
\dt

SELECT COUNT(*) FROM pokemon;
SELECT COUNT(*) FROM pokemon_descriptions;
SELECT COUNT(*) FROM pokemon_types;
SELECT COUNT(*) FROM pokemon_abilities;
SELECT COUNT(*) FROM pokemon_stats;
```

## Run the ETL pipeline

The main DAG is `pokemon_etl_pipeline`. It runs daily and has the following
task flow:

```text
extract_pokemon
        ↓
transform_pokemon_data
        ↓
validate_pokemon_data
        ↓
load_pokemon_data_to_database
```

The extract task is dynamically mapped over Pokémon IDs 1 through 151. Each
record is:

1. Retrieved from PokéAPI.
2. Transformed into rows for the four PostgreSQL tables.
3. Checked for required fields, valid IDs, types, abilities, and stats.
4. Upserted into PostgreSQL in a transaction.

To run it from the Airflow UI:

1. Open <http://localhost:8080>.
2. Find `pokemon_etl_pipeline`.
3. Enable the DAG if it is paused.
4. Click the **Run** or **Trigger DAG** button.
5. Open the task instances to inspect logs and mapped task results.

The `test_postgres_connection` DAG runs:

```sql
SELECT current_database();
```

Use it to check the Airflow-to-PostgreSQL connection configured as
`postgres_pokemon`.

The standalone example in [src/load.py](./src/load.py) can also
load one Pokémon:

```bash
astro dev bash
python -m src.load
```

## Export PostgreSQL tables to CSV

[src/export.py](./src/export.py) exports every ordinary table in
the `public` schema to a separate CSV file. It performs a client-side
`COPY ... TO STDOUT`, which is important: the Python process writes the file to
the local filesystem. Do not use PostgreSQL server-side syntax such as:

```sql
COPY pokemon TO '/home/pokemon/src/data/pokemon.csv' WITH CSV HEADER;
```

That path belongs to the PostgreSQL container and can result in
`Permission denied` or `No such file` errors.

Run the exporter from the project root:

```bash
python src/export.py
```

With the default configuration, files are written to:

```text
src/data/pokemon.csv
src/data/pokemon_descriptions.csv
src/data/pokemon_types.csv
src/data/pokemon_abilities.csv
src/data/pokemon_stats.csv
```

To export a single query:

```bash
python src/export.py \
  "SELECT * FROM pokemon ORDER BY id" \
  "src/data/pokemon_sorted.csv"
```

The exporter accepts these environment variables:

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=pokemon
export PGUSER=postgres
export PGPASSWORD=postgres
export POSTGRES_SCHEMA=public
export EXPORT_DIR=/home/pokemon/src/data
```

If Python is installed in the project virtual environment, use its interpreter
explicitly:

```bash
/home/pokemon/.pokevenv/bin/python src/export.py
```

## Python environment and dependencies

The Astro Runtime installs the dependencies from
[requirements.txt](./requirements.txt), including:

- `pandas` and `numpy`
- `requests`
- `SQLAlchemy`
- `psycopg[binary]`
- `dbt-postgres`
- Airflow PostgreSQL and Snowflake providers

For a host-side virtual environment, install dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

In VS Code, select the interpreter with **Python: Select Interpreter**. Use the
interpreter belonging to the environment where the dependencies are installed.

## Testing

Run the Astro test command from the project root:

```bash
astro dev pytest
```

For a quick Python syntax check:

```bash
python -m compileall src dags
```

Tests and local scripts should not require live PokéAPI access unless explicitly
intended. When adding tests, keep pure transformation and validation tests
separate from tests that require external services.

## Troubleshooting

### `usage: export.py ... required: query, output`

Use the current exporter without arguments to export all tables:

```bash
python src/export.py
```

Or provide both arguments for one query:

```bash
python src/export.py "SELECT * FROM pokemon" "src/data/pokemon.csv"
```

### `Permission denied` while writing a CSV

Run the exporter from Python, not with server-side PostgreSQL `COPY ... TO
'/path'`. Also choose a directory owned by your user:

```bash
export EXPORT_DIR="$PWD/src/data"
python src/export.py
```

### `connection refused` or `could not translate host name`

Check that Docker and Astro are running:

```bash
astro dev status
docker ps
```

Then verify the host. Use `localhost` from the host machine and the Docker
service hostname from a container.

### `database "pokemon" does not exist`

Create the database first, then run the table setup SQL:

```sql
CREATE DATABASE pokemon;
```

### `ModuleNotFoundError: psycopg`

Use the interpreter where the project dependencies are installed, or install
the requirements:

```bash
pip install -r requirements.txt
```

### Docker port conflicts

A service may fail to start if ports `8080` or `5432` are already occupied.
Stop the conflicting service or change the local Astro port configuration
before running `astro dev start` again.

## Stop and clean up

Stop the local services when finished:

```bash
astro dev stop
```

Do not delete the PostgreSQL volume unless you intentionally want to remove the
database data. Re-running the ETL uses upserts, so it can safely refresh
existing Pokémon records.
