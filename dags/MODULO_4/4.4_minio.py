from datetime import datetime
from airflow import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_local import S3ToLocalFilesystemOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def get_s3_hook():
    return S3Hook(aws_conn_id='my_minio_conn', region_name='us-east-1')

default_args = {
    'owner': 'Docente',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'minio_file_transfer',
    default_args=default_args,
    description='A simple DAG to transfer files to and from MinIO',
    schedule_interval='@daily',
)

upload_to_minio = LocalFilesystemToS3Operator(
    task_id='upload_to_minio',
    filename='/path/to/local/file',
    dest_key='s3_key',
    dest_bucket='my_bucket',
    replace=True,
    aws_conn_id='my_minio_conn',
    dag=dag,
)

download_from_minio = S3ToLocalFilesystemOperator(
    task_id='download_from_minio',
    s3_key='s3_key',
    local_path='/path/to/destination/file',
    bucket_name='my_bucket',
    aws_conn_id='my_minio_conn',
    dag=dag,
)

upload_to_minio >> download_from_minio
