import json
import requests
import logging
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.models import Variable
from datetime import datetime, timedelta
from pandas import json_normalize

default_args = {
    'owner': 'Docente',
    'start_date': datetime(2024, 4, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='import_soccer_players',
    default_args=default_args,
    description='DAG para importar datos de jugadores de un equipo de fútbol desde una API a MySQL',
    schedule_interval='@daily',
    tags=["MODULO_3"],
) as dag:
    
    def obtener_jugadores_futbol(id_equipo):
        url = 'https://v3.football.api-sports.io/players/squads'
        params = {'team': id_equipo}
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': Variable.get('soccer_secret_key')
        }
        respuesta = requests.get(url=url, params=params, headers=headers)
        datos = json.loads(respuesta.text)["response"][0]["players"]
        df = json_normalize(datos)
        ruta_csv = f'/opt/airflow/dags/input_data/ejemplo1_{id_equipo}.csv'
        df.to_csv(ruta_csv, index=False)
        logging.info(f"Datos exportados para el equipo {id_equipo} a {ruta_csv}.")

    def cargar_jugadores_futbol(id_equipo):
        ruta_archivo = f'/opt/airflow/dags/input_data/ejemplo1_{id_equipo}.csv'
        mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
        mysql_hook.bulk_load_custom('jugadores_futbol_ejemplo1', ruta_archivo, extra_options="FIELDS TERMINATED BY ','")
        logging.info("¡Datos cargados en MySQL con éxito!")

    inicio = EmptyOperator(task_id='inicio_ejemplo1')

    crear_tabla = MySqlOperator(
        task_id='crear_tabla_si_no_existe_ejemplo1',
        mysql_conn_id='mysql_default',
        sql="""
            CREATE TABLE IF NOT EXISTS jugadores_futbol_ejemplo1 (
                id_jugador INT,
                nombre VARCHAR(100),
                edad INT,
                numero INT,
                posicion VARCHAR(100),
                foto VARCHAR(200)
            );
            """
    )

    obtener_jugadores = PythonOperator(
        task_id='obtener_jugadores_ejemplo1',
        python_callable=obtener_jugadores_futbol,
        op_args=[100] # Informacion del PSG
    )



    cargar_jugadores = PythonOperator(
        task_id='cargar_jugadores_ejemplo1',
        python_callable=cargar_jugadores_futbol,
        op_kwargs={'id_equipo': 100} # Informacion del PSG
    )

    fin = EmptyOperator(task_id='fin_ejemplo1')


    inicio >> crear_tabla >> obtener_jugadores >> cargar_jugadores >> fin
