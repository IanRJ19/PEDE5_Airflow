import airflow
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow import DAG

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2020, 11, 18),
    'retries': 10,
    'retry_delay': timedelta(hours=1),
    'email_on_failure': False,
    'email_on_retry': False
}

# Creación del objeto DAG
with DAG('dag_proceso_spark',
            default_args=default_args,
            description='Un DAG que ejecuta dos scripts de Spark para procesamiento de datos',
            schedule_interval='0 1 * * *',  # Se ejecuta diariamente a la 1:00 AM
            catchup=False) as dag:

    # Tarea para ejecutar el script de extracción y agregación de documentos
    tarea_extraccion = BashOperator(
        task_id='extraer_y_agregar_documentos',
        bash_command='python3 /path/to/dags/spark_extraccion.py '
    )

    # Tarea para realizar transformaciones adicionales en Spark
    tarea_transformacion = BashOperator(
        task_id='transformar_datos',
        bash_command='python3 /path/to/dags/spark_transformacion.py '
    )

    # Definir dependencias
    tarea_extraccion >> tarea_transformacion  # La tarea_transformacion depende de tarea_extraccion
