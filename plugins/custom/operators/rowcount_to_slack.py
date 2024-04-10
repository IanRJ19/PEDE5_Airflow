import logging

from airflow.models.baseoperator import BaseOperator

from airflow.exceptions import AirflowException
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

class RowCountToSlackChannelOperator(BaseOperator):

    template_fields = ("table_name", "message", "channel")

    def __init__(self,
                 slack_conn: str = None,
                 mysql_conn: str = None,
                 slack_channel: str = '#airflow-notifications',
                 message: str = '',
                 table_name: str = None,
                 table_predicate: str = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        #super(RowCountToSlackChannelOperator).__init__(*args, **kwargs)
        self.slack_conn = slack_conn
        self.mysql_conn = mysql_conn
        self.message = message
        self.table_name = table_name
        self.table_predicate = table_predicate
        self.channel = slack_channel
        self.mysql_hook = None
        self.slack_hook = None

    
    def execute(self, context):
        if not isinstance(self.table_name, str):
            raise AirflowException(f"Argument 'table_name' of type { type(self.table_name) } is not a string.")
        if not isinstance(self.table_predicate, str):
            raise AirflowException(f"Argument 'table_predicate' of type { type(self.table_predicate) } is not a string.")
        
        if self.mysql_conn:
            self.mysql_hook = MySqlHook(mysql_conn_id="mysql_default")
        else:
            raise AirflowException("Argument 'mysql_conn' is not define.")

        conn = self.mysql_hook.get_conn()
        cursor = conn.cursor()
        sql = f""" SELECT COUNT(1) total_records FROM {self.table_name} {self.table_predicate} """
        logging.info(sql)
        cursor.execute(sql)
        total_records  = cursor.fetchone()[0]

        self.slack_hook =  SlackWebhookHook(slack_webhook_conn_id='slack_webhook_conn')
        self.slack_hook.send_text(text=f" :loudspeaker: {total_records} records were loaded into the table. { self.message }")
        logging.info(f"{total_records} records were loaded into the table. { self.message }")

