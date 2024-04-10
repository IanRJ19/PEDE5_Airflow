import json
import requests
import logging

from datetime import datetime, timedelta
from pandas import json_normalize
from airflow.models import Variable

def get_soccer_team_players(team_id, endpoint):
        url = endpoint
        params = {'team': team_id}
        headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': Variable.get('soccer_secret_key')
        }
        response = requests.get(url=url, params=params, headers=headers)
        response = json.loads(response.text)["response"][0]["players"]
        df = json_normalize(response)
        #df.to_csv(f'/opt/airflow/dags/input_data/{team_id}.csv', index=False, header=False, sep="\t")
        df.to_csv(f'/opt/airflow/dags/input_data/{team_id}.csv', index=False, header=False)
        logging.info(f"The file for soccer team with id: {team_id} was exported successfully.")