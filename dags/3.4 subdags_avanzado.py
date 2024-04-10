from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator
from subdags.subdag_parallel import subdag_parallel

from datetime import datetime, timedelta


default_args = {
    'owner': 'DSRP Class',
    'depends_on_past': True,
    'start_date': datetime(2023,7,31),
    'retries': 3,
    'retry_delay': timedelta(seconds=30)
}

with DAG(dag_id='subdags',
         schedule='@daily',
         catchup=False,
         default_args=default_args
         ) as dag:
    
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    init_variables = BashOperator(
        task_id='init_variables',
        bash_command='sleep 3'
    )
    
    processing = BashOperator(
        task_id='processing',
        bash_command='sleep 3'
    )
    
    task_execution = SubDagOperator(
        task_id='task_execution',
        subdag=subdag_parallel(parent_dag_id='subdags', child_dag_id='task_execution', default_args=default_args)
    )
        
    start >> init_variables >> task_execution >> processing >> end


    

