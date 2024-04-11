from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta


default_args={
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'owner': 'Docente',

}


with DAG(dag_id="dag_scheduling_complex",
            start_date=datetime(2023, 7, 24),
            catchup=False,
            schedule_interval='*/5 * * * *',  # Se ejecuta cada 5 minutos
            default_args=default_args,
            max_active_runs=1,
            dagrun_timeout=timedelta(minutes=20),
            tags=["MODULO_2"]
            ) as dag:

    # Inicio del DAG
    start = DummyOperator(task_id="start")

    # Tarea de extracción cada 5 minutos
    extract = EmptyOperator(task_id="extract")

    # Tarea de transformación con un intervalo de tiempo fijo de espera
    transform = BashOperator(task_id="transform",
                                bash_command="sleep 10")

    # Tarea de carga con un comando de bash
    load = BashOperator(task_id="load",
                        bash_command="sleep 5; echo 'The process has finished'")

    # Tarea final del DAG
    end = DummyOperator(task_id="end")

    # Tarea de limpieza sin schedule_interval en BashOperator
    cleanup = BashOperator(task_id="cleanup",
                        bash_command="echo 'Cleaning up...'")


    # Definición de dependencias y flujo de tareas
    start >> extract >> transform >> load >> end
    start >> cleanup  # Ejecuta la limpieza independientemente del flujo principal

