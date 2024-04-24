
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time

# Definimos una función para simular una tarea
def simulate_task(task_number, duration):
    print(f"Iniciando tarea {task_number}...")
    time.sleep(duration)
    print(f"Tarea {task_number} completada en {duration} segundos.")

# Definimos los detalles del DAG
with DAG(
    dag_id="dag_concurrencia",
    start_date=datetime(2024, 4, 3),
    catchup=False,
    tags=["MODULO_1"],
    schedule_interval="@daily",
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
        'owner': 'Docente'
    },
    description="Un DAG para demostrar concurrencia",
    concurrency=5,  # Permite hasta 5 tareas en paralelo
) as dag:

    # Creamos varias tareas que se pueden ejecutar en paralelo
    task1 = PythonOperator(
        task_id="task1",
        python_callable=simulate_task,
        op_args=['1', 10]  # Ejemplo: tarea 1 tarda 10 segundos
    )

    task2 = PythonOperator(
        task_id="task2",
        python_callable=simulate_task,
        op_args=['2', 15]  # Ejemplo: tarea 2 tarda 15 segundos
    )

    task3 = PythonOperator(
        task_id="task3",
        python_callable=simulate_task,
        op_args=['3', 20]  # Ejemplo: tarea 3 tarda 20 segundos
    )

    task4 = PythonOperator(
        task_id="task4",
        python_callable=simulate_task,
        op_args=['4', 5]  # Ejemplo: tarea 4 tarda 5 segundos
    )

    task5 = PythonOperator(
        task_id="task5",
        python_callable=simulate_task,
        op_args=['5', 25]  # Ejemplo: tarea 5 tarda 25 segundos
    )

    # Todas las tareas se inician al mismo tiempo, demostrando la concurrencia
    task1 >> [task2, task3, task4, task5]