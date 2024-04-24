from datetime import datetime
from pyspark.sql import SparkSession, functions as F

# Inicialización de la sesión de Spark
spark = SparkSession.builder \
    .appName("Extracción y Agregación de Documentos") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0,com.microsoft.sqlserver:mssql-jdbc:8.4.1.jre8") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1:27017/Financeiro") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1:27017/Financeiro") \
    .config("spark.driver.maxResultSize", "8g") \
    .master("spark://192.168.0.1:7077") \
    .getOrCreate()

inicio = datetime.now()

# Lectura de datos desde SQL Server
jdbcDF = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlserver://127.0.0.1:1433;databaseName=Teste") \
    .option("user", 'Teste') \
    .option("password", 'teste') \
    .option("numPartitions", 100) \
    .option("partitionColumn", "Id") \
    .option("lowerBound", 1) \
    .option("upperBound", 488777675) \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .option("dbtable", "(select Id, DataVencimento AS Vencimiento, TipoCod AS CodigoTipoDocumento, cast(recsld as FLOAT) AS Saldo from DocumentoPagar where TipoCod in ('200','17') and RecPag = 'A') T") \
    .load()

# Agrupación y agregación de datos
group = jdbcDF.select("CodigoTipoDocumento", "Vencimiento", "Saldo") \
    .groupby(["CodigoTipoDocumento", "Vencimiento"]).agg(F.sum("Saldo").alias("TotalSaldo"))

# Escritura en MongoDB
group.write.format("com.mongodb.spark.sql.DefaultSource") \
    .mode("overwrite") \
    .option("database", "Financeiro") \
    .option("collection", "Fact_DocumentoPagar") \
    .save()

termino = datetime.now()
print(f"Tiempo de ejecución: {termino - inicio}")
