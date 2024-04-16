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



# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2024, 4, 15),
    'retries': 1,
    'execution_timeout': timedelta(seconds=300)
}

def leer_archivos(ti, ruta_directorio, nombres_archivos): # TASK_ID='EXTRAER'
    dataframes = []
    dataframes_adicionales = []
    for nombre_archivo in nombres_archivos:
        archivo_completo = os.path.join(ruta_directorio, nombre_archivo)
        print(f"Procesando {nombre_archivo}")
        dataframe = pd.read_excel(archivo_completo, skiprows=4, header=[0, 1])
        dataframe_adicional = pd.read_excel(archivo_completo, nrows=3)
        dataframes.append(dataframe)
        dataframes_adicionales.append(dataframe_adicional)
    ti.xcom_push(key='dataframes', value=dataframes)
    ti.xcom_push(key='dataframes_adicionales', value=dataframes_adicionales)


def cargar_datos_mysql(ti, tabla_destino, **kwargs):
    df = ti.xcom_pull(key='df_combinado', task_ids='TRANSFORMACION.combinar_ordenar')
    ruta_archivo_temporal = '/tmp/datos_temporales.csv'
    df.to_csv(ruta_archivo_temporal, index=False, header=False)
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
    mysql_hook.bulk_load_custom(tabla_destino, ruta_archivo_temporal, extra_options="FIELDS TERMINATED BY ','")
    logging.info(f"¡Datos cargados en MySQL con éxito en la tabla {tabla_destino}!")



# Definir el DAG principal
with DAG(
    dag_id='Dag_EJEMPLO_mixto',
    default_args=default_args,
    description='Un DAG de ejemplo que combina taskgroup, xcom, sensor, triggerrules',
    schedule_interval='@daily',
    catchup=False,
    tags=["MODULO_3"],
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
        op_kwargs={'ruta_directorio': 'dags/reto_bases_info', 'nombres_archivos': ['Base_1.xlsx', 'Base_2.xlsx']}
    )


    with TaskGroup(group_id='TRANSFORMACION') as TRANSFORMACION:
        procesar = PythonOperator(
            task_id='procesar',
            python_callable=procesar_dataframes,
            provide_context=True,
            op_kwargs={'nombres_archivos': ['Base_1.xlsx', 'Base_2.xlsx']}
        )

        limpiar = PythonOperator(
            task_id='limpiar',
            provide_context=True,
            python_callable=limpiar_nombres_columnas,
        )

        filtrar = PythonOperator(
            task_id='filtrar',
            python_callable=filtrar_competencias,
            provide_context=True,
            op_kwargs={
                'competencias': ["Calidad del trabajo", "Desarrollo de relaciones", "Escrupulosidad/Minuciosidad",
                                "Flexibilidad y Adaptabilidad", "Orden y la calidad", "Orientación al Logro",
                                "Pensamiento Analítico", "Resolución de problemas", "Tesón y disciplina", "Trabajo en equipo"],
                'categorias': ["_Valor", "_Esperado", "_Brecha", "_Cumplimiento"]
            }
        )

        refinar = PythonOperator(
            task_id='refinar',
            python_callable=refinar_dataframe,
            provide_context=True,
            op_kwargs={
                'fecha_columna': 'Fecha de Finalización de Proceso (Zona horaria GMT 0)',
                'identificacion_columna': 'No. Identificación'
            },
        )

        combinar_ordenar = PythonOperator(
            task_id='combinar_ordenar',
            python_callable=combinar_y_ordenar_datos,
            provide_context=True,
            op_kwargs={'ruta': 'dags/reto_bases_info'},
        )


        procesar >> limpiar >> filtrar >> refinar >> combinar_ordenar


    CARGAR = PythonOperator(
        task_id='CARGAR',
        python_callable=cargar_datos_mysql,
        provide_context=True,
        op_kwargs={'tabla_destino': 'Base_Consolidada'}
    )


    FINAL = BashOperator(
        task_id='FINAL',
        bash_command="sleep 3; echo 'TODAS LAS TRANSFORMACIONES SE EJECUTARÓN CORRECTAMENTE'",
        trigger_rule="all_success"
    )