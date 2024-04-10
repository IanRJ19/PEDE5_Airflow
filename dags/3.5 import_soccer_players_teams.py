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
from airflow.utils.task_group import TaskGroup
from pandas import json_normalize

args_defecto = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'importar_jugadores_futbol_ejemplo2',
    default_args=args_defecto,
    description='DAG para importar datos de múltiples equipos de fútbol desde una API a MySQL',
    schedule_interval='@daily',
    tags=['fútbol', 'api', 'ejemplo2'],
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
        datos = [{'id_equipo': id_equipo, **player} for player in datos]
        df = json_normalize(datos)
        ruta_csv = f'/opt/airflow/dags/input_data/ejemplo2_{id_equipo}.csv'
        df.to_csv(ruta_csv, index=False)
        logging.info(f"Datos exportados para el equipo {id_equipo} a {ruta_csv}.")

    def cargar_jugadores_futbol(id_equipo):
        ruta_archivo = f'/opt/airflow/dags/input_data/ejemplo2_{id_equipo}.csv'
        mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
        mysql_hook.bulk_load_custom('jugadores_futbol_ejemplo2', ruta_archivo, extra_options="FIELDS TERMINATED BY ','")
        logging.info(f"¡Datos cargados en MySQL para el equipo {id_equipo} con éxito!")

    inicio = EmptyOperator(task_id='inicio_ejemplo2')
    fin = EmptyOperator(task_id='fin_ejemplo2')

    crear_tabla = MySqlOperator(
        task_id='crear_tabla_si_no_existe_ejemplo2',
        mysql_conn_id='mysql_default',
        sql="""
            CREATE TABLE IF NOT EXISTS jugadores_futbol_ejemplo2 (
                id_equipo INT,
                id_jugador INT,
                nombre VARCHAR(100),
                edad INT,
                numero INT,
                posicion VARCHAR(100),
                foto VARCHAR(200)
            );
            """
    )

    inicio >> crear_tabla

    ids_equipos = [85, 529, 30, 26]

    with TaskGroup(group_id='grupo_equipos') as grupo_equipos:
        for id_equipo in ids_equipos:
            obtener_jugadores = PythonOperator(
                task_id=f'obtener_jugadores_{id_equipo}',
                python_callable=obtener_jugadores_futbol,
                op_args=[id_equipo]
            )

            cargar_jugadores = PythonOperator(
                task_id=f'cargar_jugadores_{id_equipo}',
                python_callable=cargar_jugadores_futbol,
                op_kwargs={'id_equipo': id_equipo}
            )

            obtener_jugadores >> cargar_jugadores

    crear_tabla >> grupo_equipos >> fin
