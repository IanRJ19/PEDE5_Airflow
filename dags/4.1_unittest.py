from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def greet():
    print("Hello, Airflow!")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 1, 1)
}

dag = DAG(
    'hello_airflow',
    default_args=default_args,
    schedule_interval='@daily'
)

greet_task = PythonOperator(
    task_id='greet',
    python_callable=greet,
    dag=dag
)
