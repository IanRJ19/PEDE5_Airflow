def seleccion_columnas(ti, columnas): # TASK_ID='seleccion'
    dataframe = ti.xcom_pull(key='dataframe', task_ids='EXTRAER')
    dataframe=dataframe[columnas]
    ti.xcom_push(key='dataframe', value=dataframe)
    logging.info(f"Selección de columnas realizada")