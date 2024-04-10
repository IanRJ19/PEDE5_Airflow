import os
import pandas as pd
import datetime
import re

def leer_archivos(ruta_directorio, nombres_archivos):
    dataframes = []
    dataframes_adicionales = []
    for nombre_archivo in nombres_archivos:
        archivo_completo = os.path.join(ruta_directorio, nombre_archivo)
        print(f"Procesando {nombre_archivo}")
        dataframe = pd.read_excel(archivo_completo, skiprows=4, header=[0, 1])
        dataframe_adicional = pd.read_excel(archivo_completo, nrows=3)
        dataframes.append(dataframe)
        dataframes_adicionales.append(dataframe_adicional)
    return dataframes, dataframes_adicionales

def procesar_dataframes(dataframes, dataframes_adicionales, nombres_archivos):
    dataframes_procesados = []
    for i, dataframe in enumerate(dataframes):
        id_archivo = re.search(r'(\d+)', nombres_archivos[i]).group(1)
        dataframe['Nombre del Proceso'] = f"proceso {id_archivo}"
        dataframe_adicional = dataframes_adicionales[i]
        for j in range(3):
            dataframe[dataframe_adicional.iloc[j, 0]] = dataframe_adicional.iloc[j, 1]
        dataframe['RECORD_SOURCE'] = nombres_archivos[i]
        dataframe['LOAD_DATE'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        dataframes_procesados.append(dataframe)
    return pd.concat(dataframes_procesados)

def limpiar_nombres_columnas(df):
    nombres_columnas_limpios = []
    for col in df.columns:
        if isinstance(col, tuple):
            if "Unnamed:" in col[1] or col[1] == "" or col[1] is None:
                new_col = col[0]
            else:
                new_col = '_'.join(col)
        else:
            new_col = col
        nombres_columnas_limpios.append(new_col)
    df.columns = nombres_columnas_limpios
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    return df

def filtrar_competencias(df, competencias, categorias):
    mascara_competencias = False
    for competencia in competencias:
        for categoria in categorias:
            columna = f"{competencia}{categoria}"
            mascara_competencias |= df[columna].notna()
    return df[mascara_competencias]

def refinar_dataframe(df, fecha_columna, identificacion_columna):
    if fecha_columna in df.columns:
        df[fecha_columna] = df[fecha_columna].fillna(df["Fecha de Ingreso a Proceso (Zona horaria GMT 0)"])
    df = df.sort_values(by=fecha_columna, ascending=False)
    df = df.drop_duplicates(subset=identificacion_columna, keep='first')
    df['PROCESS_DATA'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df['CREATION_USER'] = os.getlogin()
    return df

def cargar_datos_mysql(tabla_destino, df):
    # Suponiendo que df es tu DataFrame final a cargar, por ejemplo, Base_Total
    ruta_archivo_temporal = '/tmp/datos_temporales.csv'
    
    # Guardar el DataFrame en un archivo CSV
    df.to_csv(ruta_archivo_temporal, index=False, header=False)
    
    # Crear una instancia de MySqlHook
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default', local_infile=True)
    
    # Cargar los datos en la base de datos MySQL
    mysql_hook.bulk_load_custom(tabla_destino, ruta_archivo_temporal, extra_options="FIELDS TERMINATED BY ','")
    
    logging.info(f"¡Datos cargados en MySQL con éxito en la tabla {tabla_destino}!")



# Uso del código reestructurado
ruta = r'dags\Prueba reto'
nombres_archivos = ['Base_1.xlsx', 'Base_2.xlsx']
# Leer archivos
dataframes, dataframes_adicionales = leer_archivos(ruta, nombres_archivos)
# Procesar los DataFrames leídos
Base_Total = procesar_dataframes(dataframes, dataframes_adicionales, nombres_archivos)
Base_Total = limpiar_nombres_columnas(Base_Total)

competencias = ["Calidad del trabajo", "Desarrollo de relaciones", "Escrupulosidad/Minuciosidad",
                "Flexibilidad y Adaptabilidad", "Orden y la calidad", "Orientación al Logro",
                "Pensamiento Analítico", "Resolución de problemas", "Tesón y disciplina", "Trabajo en equipo"]
categorias = ["_Valor", "_Esperado", "_Brecha", "_Cumplimiento"]

Base_Total = filtrar_competencias(Base_Total, competencias, categorias)

Base_Total = refinar_dataframe(Base_Total, 'Fecha de Finalización de Proceso (Zona horaria GMT 0)', 'No. Identificación')

Base_permanencia = pd.read_excel(os.path.join(ruta, "Base_permanencia.xlsx"))
Base_Total["No. Identificación"] = Base_Total["No. Identificación"].str.replace(' ', '', regex=True)

Base_permanencia["No. Identificación"] = Base_permanencia["No. Identificación"].str.replace(' ', '', regex=True)
Base_Total = pd.merge(Base_Total, Base_permanencia, how='inner', on='No. Identificación')

Base_Total = Base_Total.sort_values(by=["Nombre del Proceso", 'Ranking'], ascending=True)

Base_Total.to_excel("Modelo_base_consolidado.xlsx", index=False)
# Uso de la función
tabla_destino = 'Base_Consolidada'
cargar_datos_mysql(tabla_destino, Base_Total)