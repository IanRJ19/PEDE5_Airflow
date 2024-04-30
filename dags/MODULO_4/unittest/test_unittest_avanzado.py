import unittest
from airflow.models import DagBag
from datetime import datetime, timedelta

class TestAdvancedAirflowDAG(unittest.TestCase):
    def setUp(self):
        # Establece la ubicación y configuración de los DAGs a cargar, excluyendo ejemplos
        self.dagbag = DagBag(dag_folder='dags/', include_examples=False)
        self.dag = self.dagbag.get_dag(dag_id='example_advanced_unittest')

    def test_dag_loaded(self):
        """Verificar si el DAG se carga correctamente en DagBag y no hay errores."""
        self.assertDictEqual(self.dagbag.import_errors, {}, msg="DAGs con errores al cargar")
        self.assertIsNotNone(self.dag)
        self.assertEquals(self.dag.dag_id, 'example_advanced_unittest')

    def test_dependencies(self):
        """Verifica las dependencias entre tareas dentro del DAG."""
        process_task = self.dag.get_task('process_data')
        load_task = self.dag.get_task('load_data')
        self.assertTrue(process_task in load_task.upstream_list)
        self.assertTrue(load_task in process_task.downstream_list)

    def test_retry_policy(self):
        """Verifica que la política de reintentos esté configurada correctamente."""
        fetch_task = self.dag.get_task('fetch_data')
        self.assertEqual(fetch_task.retries, 2)
        self.assertEqual(fetch_task.retry_delay, timedelta(minutes=5))

    def test_schedule_interval(self):
        """Verifica que el intervalo de programación del DAG esté establecido correctamente."""
        self.assertEqual(self.dag.schedule_interval, '@daily')

    def test_catchup(self):
        """Verifica que la propiedad 'catchup' del DAG sea False."""
        self.assertFalse(self.dag.catchup)

if __name__ == '__main__':
    unittest.main()
