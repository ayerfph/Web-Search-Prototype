"""Export PostgreSQL tables or a query result to CSV files."""

import argparse
import os
from pathlib import Path

import psycopg
from psycopg import sql


DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "pokemon"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_SCHEMA = "public"
OUTPUT_DIR = Path(
    os.getenv("EXPORT_DIR", str(Path(__file__).resolve().parent / "data"))
)


def get_connection() -> psycopg.Connection:
    """Open a connection to PostgreSQL."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def copy_to_file(
    connection: psycopg.Connection,
    copy_query: sql.Composed,
    output_file: Path,
) -> None:
    """Run COPY and write its output from the client to the local filesystem."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with connection.cursor().copy(copy_query) as copy, output_file.open("wb") as file:
        for data in copy:
            file.write(data)


def export_query(
    connection: psycopg.Connection,
    query: str,
    output_file: Path,
) -> None:
    """Export a SELECT query result to a local CSV file."""
    copy_query = sql.SQL("COPY ({}) TO STDOUT WITH CSV HEADER").format(
        sql.SQL(query)  # pyright: ignore[reportArgumentType]
    )
    copy_to_file(connection, copy_query, output_file)
    print(f"Exported query results to {output_file}")


def get_table_names(connection: psycopg.Connection) -> list[str]:
    """Return ordinary table names from the configured schema."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (DB_SCHEMA,),
        )
        return [row[0] for row in cursor.fetchall()]


def export_all_tables(connection: psycopg.Connection) -> None:
    """Export every ordinary table in the configured schema."""
    table_names = get_table_names(connection)
    if not table_names:
        print(f"No tables found in schema '{DB_SCHEMA}'.")
        return

    for table_name in table_names:
        output_file = OUTPUT_DIR / f"{table_name}.csv"
        copy_query = sql.SQL("COPY {}.{} TO STDOUT WITH CSV HEADER").format(
            sql.Identifier(DB_SCHEMA),
            sql.Identifier(table_name),
        )
        copy_to_file(connection, copy_query, output_file)
        print(f"Exported {DB_SCHEMA}.{table_name} to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export PostgreSQL tables or a query result to local CSV files."
    )
    parser.add_argument("query", nargs="?", help="Optional SQL SELECT query")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Local CSV destination when query is provided",
    )
    args = parser.parse_args()

    if (args.query is None) != (args.output is None):
        parser.error("query and output must be provided together")

    connection = get_connection()
    try:
        if args.query is None:
            export_all_tables(connection)
        else:
            export_query(connection, args.query, args.output)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
