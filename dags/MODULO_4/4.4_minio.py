from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_local import S3ToLocalFilesystemOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

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

# Operador para subir archivos desde el sistema local a MinIO
upload_to_minio = LocalFilesystemToS3Operator(
    task_id='upload_to_minio',
    filename='/path/to/local/file',  # Ruta del archivo local
    dest_key='s3_key',  # Llave bajo la cual se almacenará el archivo en MinIO
    dest_bucket='my_bucket',  # Nombre del bucket en MinIO
    replace=True,  # Sobrescribir el archivo si ya existe
    aws_conn_id='my_minio_conn',  # ID de conexión configurado para MinIO
    dag=dag,
)

# Operador para descargar archivos desde MinIO al sistema local
download_from_minio = S3ToLocalFilesystemOperator(
    task_id='download_from_minio',
    s3_key='s3_key',  # Llave del archivo en MinIO
    local_path='/path/to/destination/file',  # Ruta destino en el sistema local
    bucket_name='my_bucket',  # Nombre del bucket en MinIO
    aws_conn_id='my_minio_conn',  # ID de conexión configurado para MinIO
    dag=dag,
)

# Definir dependencias: primero subir archivo y luego descargarlo
upload_to_minio >> download_from_minio




#Explicación del Código
#DAG Configuration: Se define el objeto DAG con un conjunto de argumentos por defecto que incluyen propiedades como el propietario del DAG, la dependencia de ejecuciones pasadas, la gestión de errores, y la configuración de reintento.

#LocalFilesystemToS3Operator: Este operador se utiliza para subir archivos desde un sistema local a un bucket en MinIO. Requiere especificar la ruta del archivo local, la llave en MinIO bajo la cual se guardará el archivo, el bucket de destino, y las credenciales de conexión.

#S3ToLocalFilesystemOperator: Este operador se utiliza para descargar archivos de MinIO al sistema local. Se necesita especificar la llave del archivo en MinIO, la ruta local donde se desea guardar, el bucket de origen, y las credenciales de conexión.

#Dependencies: Se establece una dependencia entre la subida y la bajada del archivo, #indicando que el archivo debe ser descargado solo después de ser subido exitosamente.