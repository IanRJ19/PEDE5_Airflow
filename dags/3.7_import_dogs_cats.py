import json
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from datetime import datetime, timedelta
from airflow.providers.mysql.hooks.mysql import MySqlHook

# Argumentos por defecto para el DAG
args_defecto = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def obtener_y_cargar_datos(api_url, table_name, file_name):
    response = requests.get(api_url)
    data = response.json()

    # Verifica si la respuesta es de la API de perros
    if 'message' in data:
        # Si es así, extrae la URL de la imagen y el estado
        data = [{'image_url': data['message'], 'status': data['status']}]
    # Verifica si la respuesta es de la API de gatos
    elif 'fact' in data:
        # Si es así, extrae el hecho sobre el gato y su longitud
        data = [{'fact': data['fact'], 'length': data['length']}]
    else:
        # Si la respuesta no está en un formato esperado, registra un error y sale de la función
        raise ValueError(f"El formato de los datos de la API no es válido: {data}")

    # Crea el DataFrame de Pandas
    df = pd.DataFrame(data)

    # Guarda el DataFrame como un archivo CSV
    file_path = f'/tmp/{file_name}.csv'
    df.to_csv(file_path, index=False, header=False)

    # Carga el archivo CSV en la base de datos MySQL
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
    mysql_hook.bulk_load_custom(table_name, file_path)


# Definición del DAG
with DAG(
    dag_id='importar_datos_animales',
    default_args=args_defecto,
    description='DAG para importar datos de animales desde APIs a MySQL',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=["MODULO_3"]
) as dag:

    crear_tabla_perros = MySqlOperator(
        task_id='crear_tabla_perros',
        mysql_conn_id='mysql_default',
        sql="""
        CREATE TABLE IF NOT EXISTS datos_perros (
            fact TEXT,
            length INT
        );
        """
    )

    crear_tabla_gatos = MySqlOperator(
        task_id='crear_tabla_gatos',
        mysql_conn_id='mysql_default',
        sql="""
        CREATE TABLE IF NOT EXISTS datos_gatos (
            fact TEXT,
            length INT
        );
        """
    )

    obtener_y_cargar_datos_perros = PythonOperator(
        task_id='obtener_y_cargar_datos_perros',
        python_callable=obtener_y_cargar_datos,
        op_args=['https://dog.ceo/api/breeds/image/random', 'datos_perros', 'perros']
    )

    obtener_y_cargar_datos_gatos = PythonOperator(
        task_id='obtener_y_cargar_datos_gatos',
        python_callable=obtener_y_cargar_datos,
        op_args=['https://catfact.ninja/fact', 'datos_gatos', 'gatos']
    )

    crear_tabla_perros >> obtener_y_cargar_datos_perros >> obtener_y_cargar_datos_gatos
    crear_tabla_gatos >> obtener_y_cargar_datos_gatos
