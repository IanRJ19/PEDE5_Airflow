import pandas as pd

dataframe=pd.read_excel(r'archivo_sensor\Modelo_base_consolidado.xlsx')

dataframe=dataframe[['Ranking','No. Identificación','Estado','Ciudad','Género','Calidad del trabajo_Valor','Desarrollo de relaciones_Valor','Escrupulosidad/Minuciosidad_Valor','Flexibilidad y Adaptabilidad_Valor','Orden y la calidad_Valor','Orientación al Logro_Valor','Pensamiento Analítico_Valor','Resolución de problemas_Valor','Tesón y disciplina_Valor','Trabajo en equipo_Valor']]

final=dataframe[dataframe['Resolución de problemas_Valor']>5.0]