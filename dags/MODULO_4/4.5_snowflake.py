from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)  # Añadir un delay entre reintento
}

# Creación del objeto DAG
dag = DAG(
    'snowflake_operations',
    default_args=default_args,
    tags=["MODULO_4"],
    description='A DAG to interact with Snowflake',
    schedule_interval='@daily',  # Se ejecuta diariamente
    catchup=False  # No realizar ejecuciones pasadas si el start date es antiguo
)

# Consulta SQL para seleccionar datos
select_query = SnowflakeOperator(
    task_id='select_data',
    sql="SELECT * FROM my_table LIMIT 10;",
    snowflake_conn_id='my_snowflake_conn',
    dag=dag,
)

# Consulta SQL para insertar datos
insert_query = SnowflakeOperator(
    task_id='insert_data',
    sql="""
    INSERT INTO my_table (id, data)
    VALUES (1, 'Sample data');
    """,
    snowflake_conn_id='my_snowflake_conn',
    dag=dag,
)

# Consulta SQL para actualizar datos
update_query = SnowflakeOperator(
    task_id='update_data',
    sql="""
    UPDATE my_table
    SET data = 'Updated data'
    WHERE id = 1;
    """,
    snowflake_conn_id='my_snowflake_conn',
    dag=dag,
)

# Definir dependencias: primero seleccionar, luego insertar, finalmente actualizar
select_query >> insert_query >> update_query

#Explicación del Código

#Configuración del DAG: Define un objeto DAG con argumentos que especifican el propietario, la política de dependencias, el manejo de fallos, y la configuración de reintentos.

#SnowflakeOperator: Se utiliza para ejecutar consultas SQL en Snowflake. Cada instancia del operador maneja una tarea específica:
#select_query: Selecciona datos de una tabla para demostrar cómo leer datos.
#insert_query: Inserta datos en la tabla, mostrando cómo añadir registros.
#update_query: Actualiza registros en la tabla, ilustrando cómo modificar datos existentes.

#Dependencies: Establece una secuencia de tareas que comienza con la selección de datos, seguida por la inserción, y finaliza con una actualización. Esto ayuda a enseñar el flujo de trabajo de manipulación de datos en bases de datos.