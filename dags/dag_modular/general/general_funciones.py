import os
import yaml
from os import path


def yaml_to_dict(config_filename):
    """
    Parses yaml file into dict from the configurations directory.
    
    :param config_filename: Name of the YAML configuration file.
    :return: dict loaded from the YAML file.
    """
    # Construye la ruta al archivo YAML ubicado en el subdirectorio 'configuraciones'.
    dir_name = path.dirname(__file__)
    path_to_file = path.join(dir_name, 'configuraciones', config_filename)

    with open(path_to_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_config(config_filename):
    """
    Retrieves the configuration dictionary from a YAML file in the configurations directory.
    
    :param config_filename: Name of the YAML configuration file to load.
    :return: Configuration dictionary.
    """
    return yaml_to_dict(config_filename)



def get_sql(filename):
    """
    Lee un archivo SQL desde el subdirectorio 'sql' y devuelve su contenido como una cadena de texto.
    
    :param filename: Nombre del archivo SQL.
    :return: Contenido del archivo SQL como cadena de texto.
    """
    # Construye la ruta al archivo SQL ubicado en el subdirectorio 'sql'.
    dir_name = os.path.dirname(__file__)
    path_to_file = os.path.join(dir_name, 'sql', filename)

    with open(path_to_file, 'r') as file:
        return file.read()

def get_md(filename):
    """
    Lee un archivo Markdown desde el directorio principal del DAG y devuelve su contenido como una cadena de texto.
    
    :param filename: Nombre del archivo Markdown.
    :return: Contenido del archivo Markdown como cadena de texto.
    """
    # Construye la ruta al archivo Markdown ubicado en el directorio actual.
    dir_name = os.path.dirname(__file__)
    path_to_file = os.path.join(dir_name, filename)

    with open(path_to_file, 'r') as file:
        return file.read()
