from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from datetime import datetime

with DAG(dag_id="depends_on_past",
         start_date=datetime(2023,7,20),
         schedule='@daily',
         catchup=True,
         max_active_runs=1) as dag:
    
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    extract = BashOperator(task_id="extract", bash_command="sleep 5")

    clean = BashOperator(task_id="clean", 
                         bash_command="sleep 10",
                         depends_on_past=True)

    load = EmptyOperator(task_id="load")

    start >> extract >> clean >> load >> end