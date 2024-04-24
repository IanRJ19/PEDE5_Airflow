from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

with DAG(
     dag_id="wait_for_downstream",
     start_date=datetime(2023, 7, 20),
     schedule_interval="@daily",
     catchup=True,
     tags=["MODULO_2"],
     max_active_runs=2,
     
) as dag:

     start = BashOperator(
          task_id="start", bash_command="sleep 10"
     )

     end = DummyOperator(task_id="end")

     extract = BashOperator(
          task_id="extract", bash_command="sleep 10"
     )

     clean = BashOperator(
          task_id="clean", bash_command="sleep 10"
     )

     load = DummyOperator(task_id="load")

     start >> extract >> clean >> load >> end
