from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="catchup",
    start_date=datetime(2024, 4, 1),  # Fecha ajustada a cerca de la actual
    catchup=True,  # Desactivamos el catchup para evitar ejecuciones automáticas pasadas
    schedule_interval='@daily',
    # default_args={'retries': 2, 'retry_delay': timedelta(minutes=5)},  # Argumentos predeterminados para las tareas
    description="Un ejemplo de DAG para demostrar funcionalidades básicas",  # Descripción del DAG
    tags=["MODULO_1"]  
    # max_active_runs=1,  # Número máximo de ejecuciones activas
    # dagrun_timeout=timedelta(hours=2),  # Tiempo máximo para la ejecución del DAG
    # params={"param1": "value1"},  # Parámetros que se pueden pasar al DAG
    # on_failure_callback=my_failure_callback_function,  # Función de callback en caso de fallo
    # on_success_callback=my_success_callback_function,  # Función de callback en caso de éxito
    # on_retry_callback=my_retry_callback_function,  # Función de callback en caso de reintento
    # concurrency=10,  # Concurrency máxima para el DAG
    # doc_md=__doc__,  # Documentación del DAG en Markdown
) as dag:

    # Tarea inicial: marca el comienzo del proceso ETL
    start = DummyOperator(task_id="start")

    # Simula la extracción de datos
    extract = BashOperator(
        task_id="extract",
        bash_command="echo 'Extrayendo datos...'; sleep 2"
    )

    # Simula la transformación de datos
    transform = BashOperator(
        task_id="transform",
        bash_command="echo 'Transformando datos...'; sleep 2"
    )

    # Simula la carga de datos
    load = BashOperator(
        task_id="load",
        bash_command="echo 'Cargando datos...'; sleep 2"
    )

    # Tarea final: marca la conclusión del proceso ETL
    end = DummyOperator(task_id="end")

    # Definimos las dependencias del flujo de tareas
    start >> extract >> transform >> load >> end