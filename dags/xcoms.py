import logging

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.decorators import task

from datetime import datetime, timedelta
from random import uniform

default_args = {
    'owner': 'DSRP Class',
    'depends_on_past': True,
    'start_date': datetime(2023,7,31),
    'retries': 3,
    'retry_delay': timedelta(seconds=30)
}

with DAG(dag_id='xcom',
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
        
        def trainig_model(ti):
            accuracy = uniform(0.1, 10.0)
            ti.xcom_push(key="model_accuracy", value=accuracy)
            logging.info(f"The accuracy of the model is: {accuracy}")
            
        training_ml_model_A = PythonOperator(task_id='training_model_A',
                                             python_callable=trainig_model)
        
        training_ml_model_B = PythonOperator(task_id='training_model_B',
                                             python_callable=trainig_model)
        
        training_ml_model_C = PythonOperator(task_id='training_model_C',
                                             python_callable=trainig_model)

    @task(task_id="choose_best_accuracy")
    def choose_best_accuracy(**context):
        #print(context)
        values = context["ti"].xcom_pull(key="model_accuracy", task_ids=["processing_models.training_model_A",
                                                                         "processing_models.training_model_B",
                                                                         "processing_models.training_model_C"])
        best_value = max(values)
        print(f"The highest accuracy is: {best_value}")

        
    start >> downloading_data >> processing_models >> choose_best_accuracy() >> end
    

