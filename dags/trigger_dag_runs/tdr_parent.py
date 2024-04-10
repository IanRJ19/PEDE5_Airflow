from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import datetime, timedelta

with DAG(dag_id='tdr_parent',
         start_date=datetime(2023,8,2),
         schedule='@daily',
         catchup=False,
         tags=['trigger_dag_runs', 'parent']
         ) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    marketing_process = TriggerDagRunOperator(
        task_id='marketing_process',
        trigger_dag_id='tdr_marketing',
        execution_date='{{ ds }}',
        reset_dag_run=True,
        wait_for_completion=True
    )

    finance_process = TriggerDagRunOperator(
        task_id='finance_process',
        trigger_dag_id='tdr_finance',
        reset_dag_run=False,
        wait_for_completion=False
    )
    
    load = BashOperator(task_id='load',
                           bash_command='sleep 5')
    
    start >> marketing_process >> finance_process >> load >> end