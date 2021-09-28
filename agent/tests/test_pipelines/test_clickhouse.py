import pytest

from .base import PipelineBaseTest


class TestClickhouse(PipelineBaseTest):
    params = {
        'test_start': [{'name': 'test_clickhouse'}, {'name': 'test_clickhouse_timestamp_ms'},
                       {'name': 'test_clickhouse_timestamp_datetime'},
                       {'name': 'test_clickhouse_advanced'}, {'name': 'test_jdbc_file_short_clickhouse'},
                       {'name': 'test_jdbc_file_full_clickhouse'}],
        'test_reset': [{'name': 'test_clickhouse'}],
        'test_force_stop': [{'name': 'test_clickhouse'}, {'name': 'test_clickhouse_timestamp_ms'},
                      {'name': 'test_clickhouse_timestamp_datetime'},
                      {'name': 'test_clickhouse_advanced'}, {'name': 'test_jdbc_file_short_clickhouse'},
                      {'name': 'test_jdbc_file_full_clickhouse'}],
        'test_output_schema': [{'name': 'test_clickhouse', 'output': 'jdbc.json', 'pipeline_type': 'clickhouse'},
                        {'name': 'test_clickhouse_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'clickhouse'},
                        {'name': 'test_clickhouse_timestamp_datetime', 'output': 'jdbc.json',
                         'pipeline_type': 'clickhouse'},
                        {'name': 'test_clickhouse_advanced', 'output': 'jdbc_file_full.json',
                         'pipeline_type': 'clickhouse'}],
        'test_delete_pipeline': [{'name': 'test_clickhouse'}, {'name': 'test_clickhouse_timestamp_ms'},
                                 {'name': 'test_clickhouse_timestamp_datetime'},
                                 {'name': 'test_clickhouse_advanced'}, {'name': 'test_jdbc_file_short_clickhouse'},
                                 {'name': 'test_jdbc_file_full_clickhouse'}],
        'test_source_delete': [{'name': 'test_jdbc_clickhouse'}, {'name': 'test_clickhouse_1'}]
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
