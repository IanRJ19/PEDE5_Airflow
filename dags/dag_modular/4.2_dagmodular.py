import pandas as pd
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from datetime import datetime,timedelta
import logging
from sqlalchemy import create_engine


# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2024, 4, 15),
    'retries': 1,
    'execution_timeout': timedelta(seconds=300)
}

# Definir el DAG principal
with DAG(
    dag_id='Dag_modular_mixto',
    default_args=default_args,
    description='Un DAG de ejemplo que combina taskgroup, xcom, sensor, triggerrules y separación de forma modular',
    schedule_interval='@daily',
    catchup=False,
    tags=["MODULO_4"],
) as dag:


    INICIO = FileSensor(
        task_id='INICIO',
        fs_conn_id='my_filesystem',
        filepath='/opt/airflow/dags/archivo_sensor/Modelo_base_consolidado.xlsx',
        poke_interval=20,  # Tiempo en segundos para la verificación
        timeout=200  # Tiempo máximo de espera en segundos
    )

    EXTRAER = PythonOperator( 
        task_id='EXTRAER',
        python_callable=leer_archivos,
        provide_context=True,
        op_kwargs={'ruta_directorio': 'dags/archivo_sensor/Modelo_base_consolidado.xlsx'}
    )


    with TaskGroup(group_id='TRANSFORMACION') as TRANSFORMACION:

        seleccion = PythonOperator(
            task_id='seleccion',
            python_callable=seleccion_columnas,
            provide_context=True,
            op_kwargs={
                'columnas': ['Ranking','No. Identificación','Estado','Ciudad','Género','Calidad del trabajo_Valor','Desarrollo de relaciones_Valor','Escrupulosidad/Minuciosidad_Valor','Flexibilidad y Adaptabilidad_Valor','Orden y la calidad_Valor','Orientación al Logro_Valor','Pensamiento Analítico_Valor','Resolución de problemas_Valor','Tesón y disciplina_Valor','Trabajo en equipo_Valor']
            }
        )

        filtrar = PythonOperator(
            task_id='filtrar',
            python_callable=filtrar_columnas,
            provide_context=True,
            op_kwargs={'valor': 5.0}
        )

  
        seleccion>> filtrar 


    CARGAR = PythonOperator(
        task_id='CARGAR',
        python_callable=cargar_datos_mysql,
        provide_context=True,
        op_kwargs={'tabla_destino': 'BASE_CONSOLIDADA'}
    )


    FINAL = BashOperator(
        task_id='FINAL',
        bash_command="sleep 3; echo 'TODAS LAS TRANSFORMACIONES Y LA CARGA A MYSQL SE EJECUTARÓN CORRECTAMENTE'",
        trigger_rule="all_success"
    )

    INICIO >> EXTRAER >> TRANSFORMACION >> CARGAR >> FINAL
