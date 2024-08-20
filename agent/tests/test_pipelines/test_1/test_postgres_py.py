import pytest

from ..test_zpipeline_base import TestPipelineBase
from ...conftest import Order


class TestPostgreSQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_postgres_py_file_short'},
                       {'name': 'test_postgres_py_file_full'}],
        'test_force_stop': [
            {'name': 'test_postgres_py_file_short',
             'check_output_file_name': 'test_postgres_py_file_full_postgres-py.json'},
            {'name': 'test_postgres_py_file_full',
             'check_output_file_name': 'test_postgres_py_file_full_postgres-py.json'},

        ],
        'test_output_schema': [
            {'name': 'test_postgres_py_file_short', 'output': 'jdbc.json', 'pipeline_type': 'postgres-py'},
            {'name': 'test_postgres_py_file_full', 'output': 'jdbc_file_full.json',
             'pipeline_type': 'postgres-py'}],
        'test_delete_pipeline': [{'name': 'test_postgres_py_file_short'}, {'name': 'test_postgres_py_file_full'}],
        'test_source_delete': [{'name': 'test_postgres_py'}]
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
