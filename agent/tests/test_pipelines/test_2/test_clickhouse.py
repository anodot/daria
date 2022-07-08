import pytest

from ..test_zpipeline_base import TestPipelineBase


class TestClickhouse(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_clickhouse'},
            {'name': 'test_clickhouse_timestamp_ms'},
            {'name': 'test_clickhouse_timestamp_datetime'},
            {'name': 'test_clickhouse_advanced'},
            {'name': 'clickhouse_tags'},
            {'name': 'test_jdbc_file_full_clickhouse'}
        ],
        'test_reset': [{'name': 'test_clickhouse'}],
        'test_force_stop': [
            {'name': 'test_clickhouse', 'check_output_file_name': 'test_clickhouse_clickhouse.json'},
            {'name': 'test_clickhouse_timestamp_ms', 'check_output_file_name': 'test_clickhouse_timestamp_ms_clickhouse.json'},
            {'name': 'test_clickhouse_timestamp_datetime', 'check_output_file_name': 'test_clickhouse_timestamp_datetime_clickhouse.json'},
            {'name': 'test_clickhouse_advanced', 'check_output_file_name': 'test_clickhouse_advanced_clickhouse.json'},
            {'name': 'clickhouse_tags', 'check_output_file_name': 'clickhouse_tags_clickhouse.json'},
            {'name': 'test_jdbc_file_full_clickhouse'}
        ],
        'test_output_schema': [
            {'name': 'test_clickhouse', 'output': 'jdbc.json', 'pipeline_type': 'clickhouse'},
            {'name': 'test_clickhouse_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'clickhouse'},
            {'name': 'test_clickhouse_timestamp_datetime', 'output': 'jdbc.json', 'pipeline_type': 'clickhouse'},
            {'name': 'test_clickhouse_advanced', 'output': 'jdbc_file_full.json', 'pipeline_type': 'clickhouse'},
            {'name': 'clickhouse_tags', 'output': 'clickhouse_tags.json', 'pipeline_type': 'clickhouse'}
        ],
        'test_delete_pipeline': [
            {'name': 'test_clickhouse'},
            {'name': 'test_clickhouse_timestamp_ms'},
            {'name': 'test_clickhouse_timestamp_datetime'},
            {'name': 'test_clickhouse_advanced'},
            {'name': 'clickhouse_tags'},
            {'name': 'test_jdbc_file_full_clickhouse'}
        ],
        'test_source_delete': [{'name': 'test_jdbc_clickhouse'}, {'name': 'test_clickhouse_1'}]
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
