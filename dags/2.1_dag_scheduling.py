from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

from datetime import datetime

with DAG(dag_id="dag_scheduling",
         start_date=datetime(2023,7,24),
         catchup=False,
         schedule='*/5 * * * *' #schedule and schedule_interval are available, but schedule_interval is going to be deprecated.
        ) as dag:

    extract = EmptyOperator(task_id="extract")

    transform = BashOperator(task_id="transform",
                             bash_command="sleep 10")

    load = BashOperator(task_id="load",
                        bash_command="sleep 5; echo 'The process hash finished'")

    extract >> transform >> load