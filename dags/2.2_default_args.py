from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta


default_args = {
    'owner': 'Squad A',
    'depends_on_past': True,
    'execution_timeout': timedelta(seconds=10),
    'retries': 3,
    'retry_delay': timedelta(seconds=30)
}


with DAG(dag_id="default_args",
         start_date=datetime(2023,7,24),
         catchup=False,
         schedule='@daily', #schedule and schedule_interval are available, but schedule_interval is going to be deprecated.
         default_args=default_args
        ) as dag:

    extract = EmptyOperator(task_id="extract", 
                            )

    transform = BashOperator(task_id="transform",
                             bash_command="sleep 20",
                             execution_timeout=timedelta(seconds=30)
                            )

    load = BashOperator(task_id="load",
                        bash_command="exit 1"
                        )

    extract >> transform >> load