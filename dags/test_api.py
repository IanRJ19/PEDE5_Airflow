import json
import requests
import pandas as pd

# API para obtener imágenes aleatorias de perros
def obtener_perros():
    response = requests.get('https://dog.ceo/api/breeds/image/random')
    data = response.json()
    print("Perros API response:")
    print(data)

# API para obtener datos aleatorios sobre gatos
def obtener_gatos():
    response = requests.get('https://catfact.ninja/fact')
    data = response.json()
    print("Gatos API response:")
    print(data)

# Probar la API de perros
print("Probando la API de perros:")
obtener_perros()

# Probar la API de gatos
print("\nProbando la API de gatos:")
obtener_gatos()
