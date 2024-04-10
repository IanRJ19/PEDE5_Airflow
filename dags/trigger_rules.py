import logging

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.decorators import task

from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup

from datetime import datetime, timedelta
from random import uniform

default_args = {
    'owner': 'DSRP Class',
    'depends_on_past': True,
    'start_date': datetime(2023,7,31),
    'retries': 1,
    'retry_delay': timedelta(seconds=10)
}

with DAG(dag_id='trigger_rules',
         schedule='@daily',
         catchup=False,
         default_args=default_args
         ) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    downloading_data = BashOperator(
        task_id='downloading_data',
        bash_command='sleep 3'
    )
    
    with TaskGroup('processing_models') as processing_models:
        
        training_ml_model_A = BashOperator(task_id='training_model_A',
                                            bash_command="exit 1")
        
        training_ml_model_B = BashOperator(task_id='training_model_B',
                                            bash_command="exit 1")
        
        training_ml_model_C = BashOperator(task_id='training_model_C',
                                            bash_command="exit 1")

    choose = BashOperator(task_id='choose',
                          bash_command="sleep 4",
                          trigger_rule=TriggerRule.ONE_SUCCESS)
    
    send_notification = BashOperator(
        task_id='send_notification',
        bash_command="sleep 3; echo 'The machine learning models have failed.'",
        trigger_rule="all_failed"
    )

    start >> downloading_data >> processing_models >> [choose, send_notification] >> end
    

