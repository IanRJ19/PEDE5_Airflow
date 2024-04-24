from datetime import datetime
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

default_args = {
    'owner': 'Docente',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'snowflake_operations',
    default_args=default_args,
    description='A DAG to interact with Snowflake',
    schedule_interval='@daily',
)

sql_query = """
SELECT * FROM my_table LIMIT 10;
"""

run_query = SnowflakeOperator(
    task_id='run_query',
    sql=sql_query,
    snowflake_conn_id='my_snowflake_conn',
    dag=dag,
)

run_query
