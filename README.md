# Curso de Apache Airflow  - PEDE5
#### Docente: Ian Rumiche Juarez
Recursos para el curso de Apache Airflow.

## Requisitos de PC
- Procesador: Core i5 o superior  
- RAM: 8GB o más
- Windows 10 o superior

## Pre-requisitos
- [Instalar Docker Desktop](https://docs.docker.com/get-docker/)
- [Instalar Visual Studio Code](https://code.visualstudio.com/download)  

## Instalacion de Apache Airflow
1. Crea una carpeta llamada **airflow-course** en el directorio de tu preferencia.
2. Clona el siguiente **[Repositorio](https://github.com/IanRJ19/PEDE3_Airflow.git)**
3. Abrir la carpeta desde Visual Studio Code
4. Abrir la terminal. **Visual Studio Code -> Terminal -> Nueva Terminal**
5. En la terminal ejecutar el siguiente comando: **` docker compose up -d `**
6. Esperar entre 5 a 7 minutos a que los contenedores estén bien desplegados.
7. Abre tu navegador y dirigite a http://localhost:8080/
    - `Usuario:` airflow
    - `Clave:` airflow

## Eliminar Docker container, images y volumes
Ejecutar los siguientes comandos en orden:
1. Para eliminar docker containers: **` docker compose down `**
2. Para eliminar docker volumes: **` docker volume prune `**
3. Para eliminar docker images: **` docker rmi -f $(docker images -aq) `**
