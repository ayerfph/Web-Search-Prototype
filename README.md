 # Pokémon Search Prototype

An end-to-end Pokémon search prototype that combines a Python ETL pipeline with a full-stack web application. The project collects Pokémon data from [PokéAPI](https://pokeapi.co/), transforms it into relational datasets, stores it in PostgreSQL, and exposes it through an Express.js API consumed by a React/Vite frontend.

## Project goals

- Build a repeatable data pipeline for Pokémon data.
- Demonstrate extraction, transformation, validation, and loading (ETL/ELT) practices.
- Store searchable data in PostgreSQL rather than relying on live API calls for every search.
- Provide a simple REST API and responsive search interface.
- Run and orchestrate data workflows with Apache Airflow and Astro CLI.
- Package local services and dependencies with Docker.

## Technology stack

| Area | Technology |
| --- | --- |
| Data source | PokéAPI |
| ETL | Python |
| Orchestration | Apache Airflow, Astro CLI |
| Database | PostgreSQL |
| Containers | Docker |
| Backend | Node.js, Express.js |
| Frontend | React, Vite |

## Architecture

```text
PokéAPI
	 │
	 ▼
Python extraction ──► transformation ──► validation ──► PostgreSQL
																													 │
																													 ▼
																								Express.js REST API
																													 │
																													 ▼
																									 React + Vite UI
```

Airflow schedules and monitors the pipeline. Docker provides a consistent environment for the orchestration and database services. The frontend and backend can be run independently during development or deployed as separate services.

## Repository structure

```text
pokemon/
├── dags/                  # Airflow DAGs and pipeline orchestration
├── src/                   # Current Python ETL implementation
│   ├── extract.py         # Retrieve data from PokéAPI
│   ├── transform.py       # Clean and shape source data
│   ├── validate.py        # Check data quality and constraints
│   ├── load.py            # Load data into PostgreSQL
│   └── export.py          # Export or inspect processed data
├── references/            # Earlier pipeline versions and database notes
├── src/data/              # Generated or sample CSV datasets
├── tests/                 # Pipeline utilities and API checks
├── Dockerfile
├── requirements.txt
└── airflow_settings.yaml

pokemon_web/
├── backend/
│   ├── src/server.js      # Express application entry point
│   ├── src/config/db.js   # PostgreSQL connection configuration
│   └── src/routes/        # Pokémon API routes
└── frontend/
		├── src/App.jsx        # React application
		├── src/App.css        # Application styles
		└── vite.config.js     # Vite configuration
```

## ETL pipeline

### 1. Extract

The extraction step calls PokéAPI and retrieves Pokémon attributes such as names, identifiers, abilities, descriptions, types, and base statistics. Requests should be handled with timeouts, error handling, and appropriate rate limiting.

### 2. Transform

The transformation step normalizes nested API responses into tabular data. The project separates related data into datasets for:

- Pokémon identity and metadata
- Types
- Abilities
- Descriptions
- Base statistics

This separation reduces duplication and makes the data easier to query and maintain.

### 3. Validate

Validation should confirm that:

- Required identifiers and names are present.
- IDs are unique and positive.
- Relationships reference existing Pokémon records.
- Numeric statistics are valid numbers within expected ranges.
- Duplicate records are removed or explicitly handled.

Invalid records should be reported before loading rather than silently inserted.

### 4. Load

The load step writes transformed data to PostgreSQL. It should be safe to rerun by using deterministic keys, upserts, or a controlled table refresh. Database credentials belong in environment variables and must not be committed to source control.

### 5. Orchestrate

The Airflow DAG coordinates the extract, transform, validate, and load tasks. Task boundaries make retries, logging, scheduling, and failure recovery visible. Astro CLI is used to run and manage the Airflow development environment.

## Data model

A normalized PostgreSQL design can include the following tables:

- `pokemon`: the canonical Pokémon record and metadata.
- `pokemon_types`: Pokémon-to-type relationships.
- `pokemon_abilities`: Pokémon-to-ability relationships.
- `pokemon_descriptions`: localized or version-specific descriptions.
- `pokemon_stats`: base statistics by Pokémon.

The `pokemon` identifier should be the parent key for related records. Index names and commonly filtered fields to support search performance.

## Backend

The Express.js service connects to PostgreSQL and exposes Pokémon data to the frontend. Typical responsibilities include:

- Parsing and validating query parameters.
- Searching by Pokémon name or ID.
- Returning related types, abilities, descriptions, and statistics.
- Returning consistent JSON responses and HTTP status codes.
- Handling database and unexpected application errors without exposing secrets.

Example endpoint contract:

```text
GET /api/pokemon?search=pika
```

```json
{
	"data": [],
	"count": 0
}
```

The exact route names and response fields should follow the implementation in `pokemon_web/backend/src/routes/pokemon.js`.

## Frontend

The React application, bundled by Vite, provides the user-facing search experience. A typical flow is:

1. The user enters a Pokémon name or identifier.
2. React requests matching records from the Express API.
3. The UI displays loading, empty, success, and error states.
4. Results show available Pokémon details from PostgreSQL.

Keep the API base URL configurable so the frontend can use a local backend in development and a deployed backend in production.

## Configuration

Use environment variables for database and service configuration. Do not commit real credentials.

Example values:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pokemon
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
API_BASE_URL=http://localhost:3000
```

Use the variable names expected by each existing application configuration file. Local `.env` files should remain ignored by Git.

## Running the project

### Start the data platform

From the `pokemon` project directory:

```bash
astro dev start
```

This starts the Astro/Airflow development environment and its configured services. Open the Airflow UI shown by Astro CLI, enable the Pokémon DAG, and trigger it manually or wait for its schedule.

### Run the Python pipeline directly

Create or activate the Python environment, install dependencies, configure PostgreSQL, and run the ETL modules in their intended order:

```bash
pip install -r requirements.txt
python src/extract.py
python src/transform.py
python src/validate.py
python src/load.py
```

The DAG is the preferred way to run the complete workflow because it provides task logs, retries, and scheduling.

### Start the backend

```bash
cd pokemon_web/backend
npm install
npm start
```

Use the development command defined in `package.json` when hot reload is required.

### Start the frontend

```bash
cd pokemon_web/frontend
npm install
npm run dev
```

Open the local URL printed by Vite.

## Operational considerations

- Respect PokéAPI usage guidance and avoid unnecessary repeated requests.
- Cache or persist source data so searches do not depend on PokéAPI availability.
- Add retries for transient network and database failures.
- Log row counts and validation failures for every pipeline run.
- Use database indexes for search fields and foreign keys.
- Keep secrets, virtual environments, build output, and generated files out of version control.
- Test extraction, transformations, validation rules, API routes, and important frontend states.

## Development workflow

1. Update the extraction or schema design.
2. Run the transformation and validation steps against a small sample.
3. Test the full DAG in Airflow.
4. Confirm the loaded records with PostgreSQL queries.
5. Start the Express API and verify its endpoints.
6. Start the Vite frontend and test search, empty, loading, and error states.

## Future improvements

- Add pagination, sorting, and advanced filters.
- Add automated unit and integration tests in CI.
- Add database migrations and explicit schema versioning.
- Add API documentation with OpenAPI.
- Add structured logs and pipeline data-quality metrics.
- Containerize the web services alongside the data platform for deployment.
