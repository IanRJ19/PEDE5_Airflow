from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta



default_args = {
    'owner': 'Docente',
    'depends_on_past': True,
    'execution_timeout': timedelta(seconds=10),
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}



# Definimos los detalles del DAG
with DAG(
    dag_id="dag_python",
    start_date=datetime(2024, 4, 3),
    end_date=datetime(2024, 12, 31),
    catchup=False,
    schedule_interval='@daily',
    default_args=default_args,
    description="Un DAG más completo con Python Operator",
    tags=["MODULO_1"]

) as dag:

    # Definimos las tareas utilizando PythonOperator
    def task_extract(**kwargs):
        a=10+25
        print(f"Extrayendo {a} datos...")
        return a

    def task_transform(**kwargs):
        ti = kwargs['ti']
        extracted_data = ti.xcom_pull(task_ids='extract')
        print(f"Transformando datos: {extracted_data}")
        return 'Datos transformados'

    def task_load(**kwargs):
        ti = kwargs['ti']
        transformed_data = ti.xcom_pull(task_ids='transform')
        print(f"Cargando datos: {transformed_data}")
        return 'Datos cargados'

    start = DummyOperator(task_id="start")

    extract = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=task_transform,
        provide_context=True,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=task_load,
        provide_context=True,
    )

    end = DummyOperator(task_id="end")

    # Definimos las dependencias del flujo de tareas
    start >> extract >> transform >> load >> end

