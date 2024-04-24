from datetime import datetime
from pyspark.sql import SparkSession, functions as F

# Inicialización de la sesión de Spark
spark = SparkSession.builder \
    .appName("Transformaciones de Datos") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0,com.microsoft.sqlserver:mssql-jdbc:8.4.1.jre8") \
    .master("spark://192.168.0.1:7077") \
    .getOrCreate()

inicio = datetime.now()

# Leer datos desde MongoDB
datos = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", "mongodb://127.0.0.1:27017/Financeiro.Fact_DocumentoPagar") \
    .load()

# Transformaciones adicionales aquí (ejemplo: normalización, filtros adicionales)
datos_transformados = datos.filter(datos.TotalSaldo > 1000) \
    .withColumn("SaldoNormalizado", F.col("TotalSaldo") / 1000)

# Guardar o procesar los datos transformados según sea necesario
datos_transformados.show()

termino = datetime.now()
print(f"Tiempo de ejecución: {termino - inicio}")
