import pandas as pd
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime,timedelta
import logging



# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2024, 4, 15),
    'retries': 1,
    'execution_timeout': timedelta(seconds=300)
}



# Definir el DAG principal
with DAG(
    dag_id='Dag_EJEMPLO_mixto',
    default_args=default_args,
    description='Un DAG de ejemplo que combina taskgroup, xcom, sensor, triggerrules',
    schedule_interval='@daily',
    catchup=False,
    tags=["MODULO_3"],
) as dag:


