from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Argumentos por defecto para el DAG
default_args = {
    'owner': 'Docente',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)  # Añadir un delay entre reintento
}

# Creación del objeto DAG
dag = DAG(
    'scala_spark_job',
    default_args=default_args,
    tags=["MODULO_4"],
    description='A DAG to run a Scala script using Spark',
    schedule_interval='@daily',  # Se ejecuta diariamente
    catchup=False  # No realizar ejecuciones pasadas si el start date es antiguo
)

# Tarea para ejecutar el script de Scala
run_scala_script = BashOperator(
    task_id='run_scala_script',
    bash_command='spark-submit --class MainClass --master local[4] /path/to/your/scala_script.jar ',
    dag=dag,
)

run_scala_script



#Explicación del Código
#Configuración del DAG: Define un objeto DAG con argumentos que especifican el propietario, la política de dependencias, el manejo de fallos, y la configuración de reintentos.

#BashOperator: Este operador se utiliza para lanzar un comando de spark-submit, que es la forma estándar de ejecutar aplicaciones Spark escritas en Scala. Aquí debes especificar la clase principal (--class MainClass) y la ubicación del archivo jar que contiene el script de Scala (/path/to/your/scala_script.jar). El --master local[4] indica que Spark debería ejecutar localmente con 4 hilos.

#Consideraciones
#Compilación de Scala: Asegúrate de que el script de Scala esté correctamente compilado en un archivo JAR antes de intentar ejecutarlo con Spark.

#Configuración de Spark: Deberás tener Spark instalado y configurado en el entorno donde se ejecuta Airflow, o apuntar a un cluster de Spark remoto si es necesario.

#Dependencias: Si tu script de Scala tiene dependencias externas, deberás incluirlas en el comando de spark-submit usando el flag --packages o asegurarte de que todas las dependencias estén en el classpath de Spark.