import json
import requests
import logging

from datetime import datetime, timedelta
from pandas import json_normalize
from airflow.providers.mysql.hooks.mysql import MySqlHook

def load_soccer_team_players(team_id, team_name):
    # This command needs to be run in MySQL: SET GLOBAL local_infile=1;
    file_path = f'/opt/airflow/dags/input_data/{team_id}.csv'
    mysql_hook = MySqlHook(mysql_conn_id="mysql_default", local_infile=True)
    #mysql_hook.bulk_load('soccer_players', file_path)
    mysql_hook.bulk_load_custom(f'{team_name}_soccer_players', file_path, extra_options="FIELDS TERMINATED BY ','")
    logging.info("Data was loaded successfully!")