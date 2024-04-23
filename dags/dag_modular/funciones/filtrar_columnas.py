def filtrar_columnas(ti, valor): # TASK_ID='filtrar'
    dataframe = ti.xcom_pull(key='dataframe', task_ids='TRANSFORMACION.seleccion')
    final=dataframe[dataframe['Resolución de problemas_Valor']>valor]
    ti.xcom_push(key='final', value=final)
    logging.info(f"Filtrado de columnas realizado")
