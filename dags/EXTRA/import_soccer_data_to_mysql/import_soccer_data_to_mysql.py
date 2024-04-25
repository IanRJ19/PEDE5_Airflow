import logging
import os
from datetime import date, datetime, timedelta

from utils.common import get_config
from utils.common import get_md
from utils.common import get_sql


from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.slack.transfers.sql_to_slack import SqlToSlackOperator
from airflow.utils.trigger_rule import TriggerRule

# Importing custom operators
from custom.operators.rowcount_to_slack import RowCountToSlackChannelOperator

# Importing python functions
from EXTRA.import_soccer_data_to_mysql.functions.get_soccer_team_players import get_soccer_team_players
from EXTRA.import_soccer_data_to_mysql.functions.load_soccer_team_players import load_soccer_team_players

# Declare configuration variables
dag_file_name = os.path.basename(__file__).split('.')[0]
dag_config = get_config(dag_file_name = dag_file_name, config_filename = 'dag_config.yaml')
pipeline_config = get_config(dag_file_name = dag_file_name, config_filename = 'pipeline_config.yaml')

env=os.getenv('ENVIRONMENT')
default_arguments = dag_config['default_args'][env]

# Getting variables of pipeline configs
endpoint = pipeline_config['endpoint']
soccer_teams_ids = pipeline_config['soccer_teams_ids']

#Airflow docstring
doc_md = get_md(dag_file_name, 'README.md')

#logging.basicConfig(level=logging.INFO)

#Declare DAG insrtance and DAG operators
with DAG(dag_file_name,
          description='Very short description (optional)',
          start_date=datetime.strptime(dag_config['dag_args'][env]["start_date"], '%Y-%m-%d'),
          max_active_runs=dag_config['dag_args'][env]["max_active_runs"],
          catchup=dag_config['dag_args'][env]["catchup"],
          tags = dag_config['tags'],
          schedule_interval=dag_config['schedule'][env],
          default_args=default_arguments,
          dagrun_timeout=timedelta(hours=dag_config["dag_run_timeout"]),
          doc_md=doc_md,
          ) as dag:
    
    ##### DECLARING THE OPERATORS ######
    
    # Declare Dummy Operators
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    
    api_availability = HttpSensor(
        task_id='api_availability',
        http_conn_id='api_soccer',
        method='GET',
        endpoint='players/squads_v2'
    )

    # confirmation_to_slack =  SlackWebhookOperator(
    #     slack_webhook_conn_id='slack_webhook_conn',
    #     task_id='confirmation_to_slack',
    #     message='The process has finished successfully. Data was loaded for {{ ds }}. :+1:',
    #     channel='#airflow_notifications',
    #     icon_emoji=':+1:'
    # )

    # results_to_slack = SqlToSlackOperator(
    #     task_id='results_to_slack',
    #     slack_conn_id='slack_webhook_conn',
    #     sql_conn_id='mysql_default',
    #     sql=get_sql(dag_file_name, 'results_to_slack.sql'),
    #     slack_channel='#airflow_notifications',
    #     slack_message='{{ results_df }}'
    # )

    row_count_to_slack = RowCountToSlackChannelOperator(
        task_id='row_count_to_slack',
        slack_conn='slack_webhook_conn',
        mysql_conn='mysql_default',
        message='The soccer players were loaded successfully.',
        table_name='dwh.soccer_players',
        table_predicate="WHERE etl_date = '20230807'"
    )
    
    
    create_table = MySqlOperator(
        task_id="create_table_if_not_exists",
        mysql_conn_id="mysql_default",
        database="dwh",
        sql=get_sql(dag_file_name, 'create_table.sql')
    )
    
    for team_name, team_id in soccer_teams_ids.items():
        create_tmp_table_by_team = MySqlOperator(
            task_id=f"create_{team_name}_tmp_table",
            mysql_conn_id="mysql_default",
            database="dwh",
            sql=get_sql(dag_file_name, 'create_tmp_table_by_team.sql'),
            params={
                'team_name': team_name
            }
        )
        
        get_soccer_players = PythonOperator(
            task_id=f'get_{team_name}_players',
            python_callable=get_soccer_team_players,
            op_args=[team_id, endpoint]
        )

        load_soccer_players = PythonOperator(
            task_id=f'load_{team_name}_players',
            python_callable=load_soccer_team_players,
            op_kwargs={
                "team_id": team_id,
                'team_name': team_name
            }
        )

        merge = MySqlOperator(
            task_id=f"merge_{team_name}_into_soccer_table",
            mysql_conn_id="mysql_default",
            database="dwh",
            sql=get_sql(dag_file_name, 'merge_into_soccer_table.sql'),
            params={
                'team_name': team_name
            }
        )
  
        start >> create_table >> api_availability >> create_tmp_table_by_team
        #create_tmp_table_by_team >> get_soccer_players >> load_soccer_players >> merge >> confirmation_to_slack >> results_to_slack >> end
        create_tmp_table_by_team >> get_soccer_players >> load_soccer_players >> merge >> row_count_to_slack >> end