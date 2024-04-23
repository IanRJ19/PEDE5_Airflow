def cargar_datos_mysql(ti,tabla_destino):
    archivo_subido = ti.xcom_pull(key='final', task_ids='TRANSFORMACION.filtrar')

    engine = create_engine("mysql+pymysql://root:dwh@mysql_dwh:3306/dwh")
    connection = engine.connect()

    with engine.begin() as connection:
        #base = pd.read_sql_query(f"SELECT * FROM Base_Consolidada", con=connection)
        archivo_subido.to_sql(name=tabla_destino, con=connection, if_exists='append', index=True)