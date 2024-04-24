from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup

from airflow.decorators import task_group

from datetime import datetime, timedelta


default_args = {
    'owner': 'Docente',
    'depends_on_past': True,
    'start_date': datetime(2023,7,31),
    'retries': 3,
    'retry_delay': timedelta(seconds=30)
}

with DAG(dag_id='taskgroups_avanzado',
         schedule='@daily',
         catchup=False,
         default_args=default_args,
         tags=["MODULO_3"]
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
    
    # with TaskGroup('task_execution') as task_execution:
    #     for i in range(1,31):
    #         task = BashOperator(task_id=f'task_{i}', # The id of these tasks would be task_group_id concatenated with task_id
    #                             bash_command='sleep 5')

    @task_group()
    def task_execution():
        for i in range(1,31):
            task = BashOperator(
                task_id=f'task_{i}', # The id of these tasks would be task_group_id concatenated with task_id
                bash_command='sleep 5')

        
    #start >> init_variables >> task_execution >> processing >> end
    start >> init_variables >> task_execution() >> processing >> end

    

