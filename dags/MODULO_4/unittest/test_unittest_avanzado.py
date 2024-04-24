import unittest
from unittest.mock import patch, MagicMock
from airflow.models import DagBag
from airflow_project.dags.my_dag import process_data

class TestMyDag(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag(dag_folder='airflow_project/dags/', include_examples=False)
        self.dag = self.dagbag.get_dag(dag_id='example_advanced_unittest')

    def test_dag_loaded(self):
        """Verificar si el DAG se carga correctamente en DagBag."""
        self.assertFalse(self.dagbag.import_errors)
        self.assertIsNotNone(self.dag)
        self.assertEquals(self.dag.dag_id, 'example_advanced_unittest')

    @patch('airflow_project.dags.my_dag.requests.get')
    def test_fetch_data(self, mock_get):
        """Prueba de la función fetch_data para asegurarse de que maneje la respuesta de la API correctamente."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = [{'id': 1, 'title': 'test title'}]
        mock_get.return_value = mock_response

        from dags.MODULO_4.unittest_avanzado import fetch_data
        response = fetch_data()
        self.assertEqual(response, [{'id': 1, 'title': 'test title'}])

    def test_process_data(self):
        """Prueba de la función process_data para verificar que procese correctamente los datos recibidos."""
        # Preparamos el ambiente de testing
        ti = MagicMock()
        ti.xcom_pull.return_value = [{'id': 1, 'title': 'test title'}]

        processed_data = process_data(ti)
        self.assertEqual(processed_data, [{'id': 1, 'title': 'test title'}])

    def test_load_data(self):
        """Prueba de la función load_data para verificar la salida correcta al cargar datos."""
        ti = MagicMock()
        ti.xcom_pull.return_value = [{'id': 1, 'title': 'test title'}]

        from dags.MODULO_4.unittest_avanzado import load_data
        with self.assertLogs(level='INFO') as log:
            load_data(ti)
            self.assertIn('Loading 1 records into the database...', log.output[0])

if __name__ == '__main__':
    unittest.main()
