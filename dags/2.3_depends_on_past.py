from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(dag_id="depends_on_past_example",
     start_date=datetime(2023, 7, 20),
     schedule_interval='@daily',
     catchup=True,
     max_active_runs=1,
     tags=["MODULO_2"]) as dag:

     start = EmptyOperator(task_id="start")
     end = EmptyOperator(task_id="end")

     # Tarea de extracción que no depende de la ejecución pasada
     extract = BashOperator(task_id="extract", bash_command="sleep 5")

     # Tarea de limpieza que depende de la ejecución pasada
     clean = BashOperator(task_id="clean",
                              bash_command="sleep 10",
                              depends_on_past=True)

     # Tarea de transformación que también depende de la ejecución pasada
     transform = BashOperator(task_id="transform",
                              bash_command="sleep 7",
                              depends_on_past=True)

     # Tarea de carga que no depende de la ejecución pasada
     load = EmptyOperator(task_id="load")

     # Definición de flujo de tareas
     start >> extract >> clean >> transform >> load >> end

     # Se añade una nueva tarea que depende del pasado para ilustrar el parámetro
     validate = BashOperator(task_id="validate",
                              bash_command="sleep 3",
                              depends_on_past=True)

     # Esta tarea se ejecutará después de 'clean' para mostrar la dependencia del pasado
     clean >> validate >> transform

