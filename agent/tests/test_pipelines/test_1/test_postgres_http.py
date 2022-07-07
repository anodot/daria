import pytest

from ..test_zpipeline_base import TestPipelineBase


class TestPostgreSQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_postgres'}, {'name': 'test_postgres_timestamp_ms'},
                       {'name': 'test_postgres_timestamp_datetime'},
                       {'name': 'test_postgres_advanced'}, {'name': 'test_jdbc_file_short_postgres'},
                       {'name': 'test_jdbc_file_full_postgres'}],
        'test_reset': [{'name': 'test_postgres'}],
        'test_force_stop': [
            {'name': 'test_postgres', 'check_output_file_name': 'test_postgres_postgres.json'},
            {'name': 'test_postgres_timestamp_ms', 'check_output_file_name': 'test_postgres_timestamp_ms_postgres.json'},
            {
                'name': 'test_postgres_timestamp_datetime',
                'check_output_file_name': 'test_postgres_timestamp_datetime_postgres.json'
            },
            {'name': 'test_postgres_advanced', 'check_output_file_name': 'test_postgres_advanced_postgres.json'},
            {'name': 'test_jdbc_file_short_postgres'},
            {'name': 'test_jdbc_file_full_postgres'}
        ],
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

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
