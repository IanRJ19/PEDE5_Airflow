from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor

from datetime import datetime, timedelta

with DAG(dag_id='ets_master',
         start_date=datetime(2024, 4, 24),
         schedule='* * * * *',
         catchup=False,
         tags=['external_task_sensor', 'master']
         ) as dag:
    
    start = EmptyOperator(task_id='start')


    sensor = ExternalTaskSensor(
        task_id='sensor',
        mode='poke',
        external_dag_id='ets_slave',
        external_task_id='load',
        poke_interval=10,
        execution_delta=timedelta(minutes=1)
    )

    extract = BashOperator(task_id='extract',
                           bash_command='sleep 4')
    
    transform = BashOperator(task_id='transform',
                           bash_command='sleep 2')
    
    load = BashOperator(task_id='load',
                           bash_command='sleep 2')
    

    end = EmptyOperator(task_id='end')
    
    start >> sensor >> extract >> transform >> load >> end