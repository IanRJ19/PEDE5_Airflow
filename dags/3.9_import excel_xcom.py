import os
import pandas as pd
import re
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.mysql.hooks.mysql import MySqlHook
import logging
from datetime import datetime

# task_instance=ti

def leer_archivos(ti, ruta_directorio, nombres_archivos):
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


def procesar_dataframes(ti, nombres_archivos):
    dataframes = ti.xcom_pull(key='dataframes', task_ids='EXTRAER')
    dataframes_adicionales = ti.xcom_pull(key='dataframes_adicionales', task_ids='EXTRAER')
    dataframes_procesados = []
    for i, dataframe in enumerate(dataframes):
        id_archivo = re.search(r'(\d+)', nombres_archivos[i]).group(1)
        dataframe['Nombre del Proceso'] = f"proceso {id_archivo}"
        dataframe_adicional = dataframes_adicionales[i]
        for j in range(3):
            dataframe[dataframe_adicional.iloc[j, 0]] = dataframe_adicional.iloc[j, 1]
        dataframe['RECORD_SOURCE'] = nombres_archivos[i]
        dataframe['LOAD_DATE'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        dataframes_procesados.append(dataframe)
    ti.xcom_push(key='dataframes_procesados', value=pd.concat(dataframes_procesados))


def limpiar_nombres_columnas(ti, **kwargs):
    df = ti.xcom_pull(key='dataframes_procesados', task_ids='procesar_dataframes')
    nombres_columnas_limpios = []
    for col in df.columns:
        if isinstance(col, tuple):
            if "Unnamed:" in col[1] or col[1] == "" or col[1] is None:
                new_col = col[0]
            else:
                new_col = '_'.join(col)
        else:
            new_col = col
        nombres_columnas_limpios.append(new_col)
    df.columns = nombres_columnas_limpios
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    ti.xcom_push(key='dataframes_limpios', value=df)


def filtrar_competencias(ti, competencias, categorias, **kwargs):
    df = ti.xcom_pull(key='dataframes_limpios', task_ids='limpiar_nombres_columnas')
    mascara_competencias = False
    for competencia in competencias:
        for categoria in categorias:
            columna = f"{competencia}{categoria}"
            mascara_competencias |= df[columna].notna()
    df_filtrado = df[mascara_competencias]
    ti.xcom_push(key='dataframes_filtrados', value=df_filtrado)


def refinar_dataframe(ti, fecha_columna, identificacion_columna, **kwargs):
    df = ti.xcom_pull(key='dataframes_filtrados', task_ids='filtrar_competencias')
    if fecha_columna in df.columns:
        df[fecha_columna] = df[fecha_columna].fillna(df["Fecha de Ingreso a Proceso (Zona horaria GMT 0)"])
    df = df.sort_values(by=fecha_columna, ascending=False)
    df = df.drop_duplicates(subset=identificacion_columna, keep='first')
    df['PROCESS_DATA'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    df['CREATION_USER'] = os.getlogin()
    ti.xcom_push(key='dataframe_refinado', value=df)



def combinar_y_ordenar_datos(ti, ruta):
    df = ti.xcom_pull(key='dataframes_procesados', task_ids=['TRANSFORMACION.procesar', 'TRANSFORMACION.limpiar', 'TRANSFORMACION.filtrar', 'TRANSFORMACION.procesar_dataframe'])
    base_permanencia = pd.read_excel(os.path.join(ruta, "Base_permanencia.xlsx"))
    df["No. Identificación"] = df["No. Identificación"].str.replace(' ', '', regex=True)
    base_permanencia["No. Identificación"] = base_permanencia["No. Identificación"].str.replace(' ', '', regex=True)
    df_combinado = pd.merge(df, base_permanencia, how='inner', on='No. Identificación')
    df_combinado = df_combinado.sort_values(by=["Nombre del Proceso", 'Ranking'], ascending=True)
    ti.xcom_push(key='df_combinado', value=df_combinado)




def cargar_datos_mysql(ti, tabla_destino, **kwargs):
    df = ti.xcom_pull(key='df_combinado', task_ids='TRANSFORMACION.combinar_y_ordenar_datos')
    ruta_archivo_temporal = '/tmp/datos_temporales.csv'
    df.to_csv(ruta_archivo_temporal, index=False, header=False)
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
    mysql_hook.bulk_load_custom(tabla_destino, ruta_archivo_temporal, extra_options="FIELDS TERMINATED BY ','")
    logging.info(f"¡Datos cargados en MySQL con éxito en la tabla {tabla_destino}!")




# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'start_date': datetime(2024, 4, 10),
    'retries': 1
}



# Definir el DAG principal
with DAG(
    dag_id='ETL_XCOM',
    default_args=default_args,
    description='Un DAG de ejemplo que utiliza xcoms',
    schedule_interval='@daily',
    catchup=False,
    tags=["MODULO_3"],
) as dag:

    inicio = DummyOperator(task_id='inicio')

    EXTRAER = PythonOperator(
        task_id='EXTRAER',
        python_callable=leer_archivos,
        op_kwargs={'ruta_directorio': 'dags/bases_info', 'nombres_archivos': ['Base_1.xlsx', 'Base_2.xlsx']}
    )

    with TaskGroup(group_id='TRANSFORMACION') as TRANSFORMACION:
        procesar = PythonOperator(
            task_id='procesar',
            python_callable=procesar_dataframes,
            op_kwargs={'nombres_archivos': ['Base_1.xlsx', 'Base_2.xlsx']}
        )

        limpiar = PythonOperator(
            task_id='limpiar',
            python_callable=limpiar_nombres_columnas,
        )

        filtrar = PythonOperator(
            task_id='filtrar_competencias',
            python_callable=filtrar_competencias,
            op_kwargs={
                'competencias': ["Calidad del trabajo", "Desarrollo de relaciones", "Escrupulosidad/Minuciosidad",
                                "Flexibilidad y Adaptabilidad", "Orden y la calidad", "Orientación al Logro",
                                "Pensamiento Analítico", "Resolución de problemas", "Tesón y disciplina", "Trabajo en equipo"],
                'categorias': ["_Valor", "_Esperado", "_Brecha", "_Cumplimiento"]
            }
        )

        refinar = PythonOperator(
            task_id='procesar_dataframe',
            python_callable=refinar_dataframe,
            op_kwargs={
                'fecha_columna': 'Fecha de Finalización de Proceso (Zona horaria GMT 0)',
                'identificacion_columna': 'No. Identificación'
            }
        )

        combinar_ordenar = PythonOperator(
            task_id='combinar_y_ordenar_datos',
            python_callable=combinar_y_ordenar_datos,
            op_kwargs={'ruta': 'dags/bases_info'}
        )

        procesar >> limpiar >> filtrar >> refinar >> combinar_ordenar

    CARGAR = PythonOperator(
        task_id='CARGAR',
        python_callable=cargar_datos_mysql,
        op_kwargs={'tabla_destino': 'Base_Consolidada'}
    )

    final = DummyOperator(task_id='final')

    inicio >> EXTRAER >> TRANSFORMACION >> CARGAR >> final
