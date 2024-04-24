from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta


dag = DAG(dag_id="task_concurrency",
            start_date=datetime(2023,7,24),
            schedule="@daily",
            default_args={
                'retries': 1,
                'retry_delay': timedelta(minutes=1),
                'owner': 'Docente'},
            catchup=False,
            max_active_tasks=2,
            tags=["MODULO_1"])

start = EmptyOperator(dag=dag, task_id="start")
end = EmptyOperator(dag=dag, task_id="end")

process_a = BashOperator(dag=dag, task_id="process_a", bash_command="sleep 5")
process_b = BashOperator(dag=dag, task_id="process_b", bash_command="sleep 5")
process_c = BashOperator(dag=dag, task_id="process_c", bash_command="sleep 5")
process_d = BashOperator(dag=dag, task_id="process_d", bash_command="sleep 5")
process_e = BashOperator(dag=dag, task_id="process_e", bash_command="sleep 5")

load = EmptyOperator(dag=dag, task_id="load")

start >> [process_e, process_a, process_c, process_b, process_d] >> load >> end