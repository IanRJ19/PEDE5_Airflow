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
import os


# IMPORTANDO FUNCIONES GENERALES
from dags.dag_modular.general.general_funciones import yaml_to_dict
from dags.dag_modular.general.general_funciones import get_config
from dags.dag_modular.general.general_funciones import get_sql
from dags.dag_modular.general.general_funciones import get_md

# IMPORTANDO FUNCIONES
from dags.dag_modular.funciones.cargar_datos_mysql import cargar_datos_mysql
from dags.dag_modular.funciones.filtrar_columnas import filtrar_columnas
from dags.dag_modular.funciones.leer_archivos import leer_archivos
from dags.dag_modular.funciones.seleccion_columnas import seleccion_columnas


# IMPORTANDO CONFIGURACIONES
config_cargar = get_config(dag_file_name = dag_modular, config_filename = 'config_cargar.yaml')
config_extraer = get_config(dag_file_name = dag_modular, config_filename = 'config_extraer.yaml')
config_filtrar = get_config(dag_file_name = dag_modular, config_filename = 'config_filtrar.yaml')
config_final = get_config(dag_file_name = dag_modular, config_filename = 'config_final.yaml')
config_inicio = get_config(dag_file_name = dag_modular, config_filename = 'config_inicio.yaml')
config_seleccion = get_config(dag_file_name = dag_modular, config_filename = 'config_seleccion.yaml')
general_config = get_config(dag_file_name = dag_modular, config_filename = 'general_config.yaml')


# Declare configuration variables
dag_file_name = os.path.basename(__file__).split('.')[0]
env=os.getenv('ENVIRONMENT')
default_arguments = dag_config['default_args'][env]

# Getting variables of pipeline configs
endpoint = pipeline_config['endpoint']
soccer_teams_ids = pipeline_config['soccer_teams_ids']

#Airflow docstring
doc_md = get_md(dag_file_name, 'README.md')


# Definir el DAG principal
with DAG(
    dag_id='dag_modular',
    default_args=general_config,
    tags=["MODULO_4"],
) as dag:


    INICIO = FileSensor(
        task_id='INICIO',
        fs_conn_id='my_filesystem',
    )

    EXTRAER = PythonOperator( 
        task_id='EXTRAER',
        python_callable=leer_archivos,
        provide_context=True,
    )

    with TaskGroup(group_id='TRANSFORMACION') as TRANSFORMACION:

        seleccion = PythonOperator(
            task_id='seleccion',
            python_callable=seleccion_columnas,
            provide_context=True,
        )

        filtrar = PythonOperator(
            task_id='filtrar',
            python_callable=filtrar_columnas,
            provide_context=True,
            
        )
        seleccion>> filtrar 


    CARGAR = PythonOperator(
        task_id='CARGAR',
        python_callable=cargar_datos_mysql,
        provide_context=True,
        
    )

    FINAL = BashOperator(
        task_id='FINAL',
    )

    INICIO >> EXTRAER >> TRANSFORMACION >> CARGAR >> FINAL
