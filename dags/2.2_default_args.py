from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'depends_on_past': True,
    'execution_timeout': timedelta(seconds=10),
    'retries': 3,
    'retry_delay': timedelta(seconds=30),
    'email_on_failure': False,
    'email_on_retry': False,
    'max_active_runs': 1
}

def dummy_python_task():
    # Función de ejemplo para PythonOperator
    print("Ejecutando una tarea de Python")

with DAG(dag_id="default_args",
         start_date=datetime(2023, 7, 24),
         catchup=False,
         schedule_interval='@daily',
         default_args=default_args,
         tags=["MODULO_2"]
        ) as dag:

    # Tarea de extracción
    extract = EmptyOperator(task_id="extract")

    # Tarea de transformación con BashOperator
    transform = BashOperator(task_id="transform",
                             bash_command="sleep 20",
                             execution_timeout=timedelta(seconds=30)
                            )

    # Tarea de carga con BashOperator
    load = BashOperator(task_id="load",
                        bash_command="exit 1"
                        )

    # Tarea adicional usando PythonOperator
    analyze = PythonOperator(task_id='analyze',
                             python_callable=dummy_python_task
                             )

    # Definición de dependencias y flujo de tareas
    extract >> transform >> load
    extract >> analyze  # Agrega una nueva rama en el flujo de tareas

