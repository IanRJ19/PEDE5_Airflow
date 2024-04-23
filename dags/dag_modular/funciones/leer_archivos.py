def leer_archivos(ti, ruta_directorio): # TASK_ID='EXTRAER'
    dataframe=pd.read_excel(ruta_directorio)
    ti.xcom_push(key='dataframe', value=dataframe)
    logging.info(f"Archivo leído con éxito")

