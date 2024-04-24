import pandas as pd
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from datetime import datetime,timedelta,timezone
from sqlalchemy import create_engine


# IMPORTANDO FUNCIONES GENERALES
#from dags.dag_modular.general.general_funciones import get_sql
from dag_modular.general.general_funciones import get_config
from dag_modular.general.general_funciones import get_md

# IMPORTANDO FUNCIONES
from dag_modular.funciones.cargar_datos_mysql import cargar_datos_mysql
from dag_modular.funciones.filtrar_columnas import filtrar_columnas
from dag_modular.funciones.leer_archivos import leer_archivos
from dag_modular.funciones.seleccion_columnas import seleccion_columnas

# IMPORTANDO CONFIGURACIONES
config_cargar = get_config('config_cargar.yaml')
config_extraer = get_config('config_extraer.yaml')
config_filtrar = get_config('config_filtrar.yaml')
config_final = get_config('config_final.yaml')
config_inicio = get_config('config_inicio.yaml')
config_seleccion = get_config('config_seleccion.yaml')
general_config = get_config( 'general_config.yaml')

# IMPORTANDO CARACTERISTICAS DE EJECUCIÓN
default_args = get_config( 'general_config.yaml')['default_args']['dev']
dag_caracteristicas= get_config( 'general_config.yaml')['dag_caracteristicas']['dev']




# IMPORTANDO MARKDOWN
doc_md = get_md( 'README.md')


# Definir el DAG principal
with DAG(
    dag_id='dag_modular',
    default_args=default_args,
    tags=["MODULO_4"],
    schedule_interval= dag_caracteristicas['schedule_interval'],
    start_date= datetime.strptime(dag_caracteristicas['start_date'], '%Y-%m-%d'),
    max_active_runs= dag_caracteristicas['max_active_runs'],
    catchup=dag_caracteristicas['catchup'],
    max_active_tasks= dag_caracteristicas['max_active_tasks']   ,
    description= dag_caracteristicas['description']

) as dag:


    INICIO = FileSensor(
        task_id='INICIO',
        fs_conn_id='my_filesystem',
        filepath=config_inicio['filepath'],
        poke_interval=config_inicio['poke_interval'],
        timeout=config_inicio['timeout']
    )

    EXTRAER = PythonOperator( 
        task_id='EXTRAER',
        python_callable=leer_archivos,
        provide_context=True,
        op_kwargs=config_extraer['op_kwargs']

    )

    with TaskGroup(group_id='TRANSFORMACION') as TRANSFORMACION:

        seleccion = PythonOperator(
            task_id='seleccion',
            python_callable=seleccion_columnas,
            provide_context=True,
            op_kwargs=config_seleccion['op_kwargs']
        )

        filtrar = PythonOperator(
            task_id='filtrar',
            python_callable=filtrar_columnas,
            provide_context=True,
            op_kwargs=config_seleccion['valor']
            
        )
        seleccion>> filtrar 


    CARGAR = PythonOperator(
        task_id='CARGAR',
        python_callable=cargar_datos_mysql,
        provide_context=True,
        op_kwargs=config_cargar['op_kwargs']
        
    )

    FINAL = BashOperator(
        task_id='FINAL',
        bash_command=config_final['bash_command'],
        trigger_rule=config_final['trigger_rule']
    )

    INICIO >> EXTRAER >> TRANSFORMACION >> CARGAR >> FINAL
