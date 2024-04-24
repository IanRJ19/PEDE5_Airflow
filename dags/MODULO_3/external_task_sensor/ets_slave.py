from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor

from datetime import datetime, timedelta

with DAG(dag_id='ets_slave',
         start_date=datetime(2023,8,3,0,54),
         schedule='*/2 * * * *',
         catchup=True,
         tags=['external_task_sensor', 'slave']
         ) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    extract = BashOperator(task_id='extract',
                           bash_command='sleep 4')
    
    transform = BashOperator(task_id='transform',
                           bash_command='sleep 2')
    
    load = BashOperator(task_id='load',
                           bash_command='sleep 40')
    
    start >> extract >> transform >> load >> end