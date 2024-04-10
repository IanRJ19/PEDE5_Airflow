
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

def enviar_valor(ti):
    valor = "hola desde tarea1"
    ti.xcom_push(key='mi_clave', value=valor)

def recibir_valor(ti):
    valor = ti.xcom_pull(task_ids='tarea1', key='mi_clave')
    print(valor)




with DAG('mi_dag_xcom',
         start_date=datetime(2022, 1, 1),
         schedule_interval='@daily',
         catchup=False) as dag:

    tarea1 = PythonOperator(
        task_id='enviar_valor',
        python_callable=enviar_valor,
    )

    tarea2 = PythonOperator(
        task_id='recibir_valor',
        python_callable=recibir_valor,
    )

    tarea1 >> tarea2
