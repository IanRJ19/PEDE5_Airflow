# airflow_project/tests/test_my_dag.py
import unittest
from unittest.mock import patch
from airflow.models import DagBag, TaskInstance
from airflow.utils.state import State
from datetime import datetime

class TestMyDag(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_dag_loaded(self):
        dag = self.dagbag.get_dag('example_advanced_unittest')
        self.assertTrue(dag is not None)
        self.assertEqual(len(dag.tasks), 3)

    @patch('requests.get')
    def test_fetch_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1, "value": "data"}]
        
        task = self.dagbag.get_dag('example_advanced_unittest').get_task('fetch_data')
        ti = TaskInstance(task=task, execution_date=datetime.now())
        ti.run(ignore_ti_state=True)
        self.assertEqual(ti.xcom_pull(task_ids='fetch_data'), [{"id": 1, "value": "data"}])

if __name__ == '__main__':
    unittest.main()
