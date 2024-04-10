from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2023, 1, 1),
    'retries': 1
}

# Definir el DAG principal
with DAG(
    dag_id='ejemplo_taskgroup',
    default_args=default_args,
    description='Un DAG de ejemplo que utiliza TaskGroup',
    schedule_interval='@daily',
    catchup=False,
    tags=["MODULO_3"],
) as dag:

    inicio = DummyOperator(
        task_id='inicio'
    )

    # Definir un TaskGroup
    with TaskGroup(group_id='grupo_de_tareas') as grupo_de_tareas:
        tarea1 = DummyOperator(
            task_id='tarea1'
        )

        tarea2 = DummyOperator(
            task_id='tarea2'
        )

        tarea3 = DummyOperator(
            task_id='tarea3'
        )

        # Definir dependencias dentro del TaskGroup
        tarea1 >> tarea2 >> tarea3

    final = DummyOperator(
        task_id='final'
    )

    # Definir las dependencias del DAG
    inicio >> grupo_de_tareas >> final
