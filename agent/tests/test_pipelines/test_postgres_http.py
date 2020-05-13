import pytest

from ..fixtures import cli_runner
from .test_zpipeline_base import pytest_generate_tests, TestPipelineBase


class TestPostgreSQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_with_file': [{'file_name': 'jdbc_pipelines_postgres'}],
        'test_create_source_with_file': [{'file_name': 'postgres_sources'}],
        'test_start': [{'name': 'test_postgres'}, {'name': 'test_postgres_timestamp_ms'},
                       {'name': 'test_postgres_timestamp_datetime'},
                       {'name': 'test_postgres_advanced'}, {'name': 'test_jdbc_file_short_postgres'},
                       {'name': 'test_jdbc_file_full_postgres'}],
        'test_reset': [{'name': 'test_postgres'}],
        'test_stop': [{'name': 'test_postgres'}, {'name': 'test_postgres_timestamp_ms'},
                      {'name': 'test_postgres_timestamp_datetime'},
                      {'name': 'test_postgres_advanced'}, {'name': 'test_jdbc_file_short_postgres'},
                      {'name': 'test_jdbc_file_full_postgres'}],
        'test_output': [{'name': 'test_postgres', 'output': 'jdbc.json', 'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_timestamp_datetime', 'output': 'jdbc.json',
                         'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_advanced', 'output': 'jdbc_file_full.json',
                         'pipeline_type': 'postgres'},
                        {'name': 'test_jdbc_file_short_postgres', 'output': 'jdbc.json', 'pipeline_type': 'postgres'},
                        {'name': 'test_jdbc_file_full_postgres', 'output': 'jdbc_file_full.json', 'pipeline_type': 'postgres'}],
        'test_delete_pipeline': [{'name': 'test_postgres'}, {'name': 'test_postgres_timestamp_ms'},
                                 {'name': 'test_postgres_timestamp_datetime'},
                                 {'name': 'test_postgres_advanced'}, {'name': 'test_jdbc_file_short_postgres'},
                                 {'name': 'test_jdbc_file_full_postgres'}],
        'test_source_delete': [{'name': 'test_jdbc_postgres'}, {'name': 'test_postgres_1'}]
    }

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
