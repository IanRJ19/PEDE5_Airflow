from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from datetime import datetime

with DAG(dag_id="wait_for_downstream",
         start_date=datetime(2023,7,20),
         schedule='@daily',
         catchup=True,
         max_active_runs=2) as dag:
    
    start = BashOperator(task_id="start", 
                           bash_command="sleep 10", wait_for_downstream=True)
    
    end = EmptyOperator(task_id="end")

    extract = BashOperator(task_id="extract", 
                           bash_command="sleep 10")

    clean = BashOperator(task_id="clean", 
                         bash_command="sleep 10")

    load = EmptyOperator(task_id="load")

    start >> extract >> clean >> load >> end