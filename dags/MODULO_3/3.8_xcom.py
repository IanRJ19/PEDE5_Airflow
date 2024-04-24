
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

#task_instance=ti


def enviar_valor(ti):
    valor = "hola desde tarea1"
    ti.xcom_push(key='LLAVE_EJEMPLO', value=valor)

def recibir_valor(ti):
    resultado = ti.xcom_pull(task_ids='tarea1', key='LLAVE_EJEMPLO') #=valor
    ti.xcom_push(key='LLAVE_FUNCION2', value=resultado)

def recibir_valor_siguiente(ti):
    final = ti.xcom_pull(task_ids='tarea2', key='LLAVE_FUNCION2') #=resultado
    print(final)



with DAG('mi_dag_xcom',
         start_date=datetime(2024, 4, 10),
         schedule_interval='@daily',
         catchup=False) as dag:

    tarea1 = PythonOperator(
        task_id='tarea1',
        python_callable=enviar_valor,
        provide_context=True,
    )

    tarea2 = PythonOperator(
        task_id='tarea2',
        python_callable=recibir_valor,
        provide_context=True,
    )

    tarea3 = PythonOperator(
        task_id='tarea3',
        python_callable=recibir_valor_siguiente,
        provide_context=True,
    )

    tarea1 >> tarea2 >> tarea3
