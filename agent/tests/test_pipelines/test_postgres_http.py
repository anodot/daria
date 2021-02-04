import pytest

from .test_zpipeline_base import TestPipelineBase, get_expected_schema_output
from ..conftest import get_output


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
        'test_force_stop': [{'name': 'test_postgres'}, {'name': 'test_postgres_timestamp_ms'},
                      {'name': 'test_postgres_timestamp_datetime'},
                      {'name': 'test_postgres_advanced'}, {'name': 'test_jdbc_file_short_postgres'},
                      {'name': 'test_jdbc_file_full_postgres'}],
        'test_output_schema': [{'name': 'test_postgres', 'output': 'jdbc.json', 'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_timestamp_datetime', 'output': 'jdbc.json',
                         'pipeline_type': 'postgres'},
                        {'name': 'test_postgres_advanced', 'output': 'jdbc_file_full.json',
                         'pipeline_type': 'postgres'}],
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

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_start(self, cli_runner, name):
        super().test_start(cli_runner, name)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_output(self, name, pipeline_type, output):
        pytest.skip()
