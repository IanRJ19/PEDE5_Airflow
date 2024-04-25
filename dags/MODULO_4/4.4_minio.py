from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_sql import S3ToSqlOperator

# Función para obtener el conector a MinIO usando S3Hook
def get_s3_hook():
    # Especificar el ID de conexión a AWS que se ha configurado en Airflow para MinIO
    return S3Hook(aws_conn_id='my_minio_conn', region_name='us-east-1')

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
    'minio_file_transfer',
    default_args=default_args,
    tags=["MODULO_4"],
    description='A simple DAG to transfer files to and from MinIO',
    schedule_interval='@daily',  # Se ejecuta diariamente
    catchup=False  # No realizar ejecuciones pasadas si el start date es antiguo
)



# Operador para descargar archivos desde MinIO al sistema local
download_from_minio = LocalFilesystemToS3Operator(
    task_id='download_from_minio',
    filename='/path/to/your/local/file',  
    dest_key='s3_key',  
    dest_bucket='my_bucket',  
    aws_conn_id='aws_default', 
    replace=False, 
    dag=dag
    # ID de conexión configurado para MinIO,
)

enviar_to_sql = S3ToSqlOperator(
    task_id='enviar_to_sql',
    schema=None ,
    table='tabla' ,
    s3_bucket='bucket' ,
    s3_key='llave' ,
    sql_conn_id='cadena_conexion' ,
    aws_conn_id='aws_default' ,
    parser='parser',
    dag=dag
)




# Definir dependencias: primero subir archivo y luego descargarlo
download_from_minio >> enviar_to_sql




#Explicación del Código
#DAG Configuration: Se define el objeto DAG con un conjunto de argumentos por defecto que incluyen propiedades como el propietario del DAG, la dependencia de ejecuciones pasadas, la gestión de errores, y la configuración de reintento.

#LocalFilesystemToS3Operator: Este operador se utiliza para subir archivos desde un sistema local a un bucket en MinIO. Requiere especificar la ruta del archivo local, la llave en MinIO bajo la cual se guardará el archivo, el bucket de destino, y las credenciales de conexión.

#S3ToLocalFilesystemOperator: Este operador se utiliza para descargar archivos de MinIO al sistema local. Se necesita especificar la llave del archivo en MinIO, la ruta local donde se desea guardar, el bucket de origen, y las credenciales de conexión.

#Dependencies: Se establece una dependencia entre la subida y la bajada del archivo, #indicando que el archivo debe ser descargado solo después de ser subido exitosamente.