from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.subdag import SubDagOperator
from datetime import datetime, timedelta

# Definir la función que creará un sub-DAG
def subdag(parent_dag_id, child_dag_id, default_args):
    with DAG(
        dag_id=f'{parent_dag_id}.{child_dag_id}',
        default_args=default_args,
        schedule_interval="@daily",
        tags=["MODULO_3"]
    ) as subdag:
        tarea1 = DummyOperator(
            task_id='tarea1'
        )

        tarea2 = DummyOperator(
            task_id='tarea2'
        )

        tarea3 = DummyOperator(
            task_id='tarea3'
        )

        tarea1 >> tarea2 >> tarea3

    return subdag

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG principal
with DAG(
    dag_id='ejemplo_subdags',
    default_args=default_args,
    description='Un DAG de ejemplo que utiliza SubDagOperator',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    inicio = DummyOperator(
        task_id='inicio'
    )

    # Crear un SubDagOperator para representar las subtareas
    subdag_tareas = SubDagOperator(
        task_id='subdag_tareas',
        subdag=subdag('ejemplo_subdags', 'subdag_tareas', default_args),
    )

    final = DummyOperator(
        task_id='final'
    )

    inicio >> subdag_tareas >> final
