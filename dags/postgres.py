from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id="test_postgres_connection",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    test_connection = SQLExecuteQueryOperator(
        task_id="test_postgres",
        conn_id="postgres_pokemon",
        sql="SELECT current_database();",
    )