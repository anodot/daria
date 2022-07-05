import pytest

from ..test_zpipeline_base import TestPipelineBase, get_schema_id
from ...conftest import get_output


class TestMySQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'},
                       {'name': 'test_mysql_timestamp_datetime'},
                       {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short_mysql'},
                       {'name': 'test_jdbc_file_full_mysql'}, {'name': 'test_mysql_timezone_datetime'},
                       {'name': 'test_mysql_no_schema'}, {'name': 'test_watermark_local_timezone'},
                       {'name': 'test_jdbc_no_timestamp_condition'}],
        'test_reset': [{'name': 'test_mysql'}],
        'test_force_stop': [
            {'name': 'test_mysql'},
            {'name': 'test_mysql_timestamp_ms'},
            {'name': 'test_mysql_timestamp_datetime'},
            {
                'name': 'test_mysql_advanced',
                'check_output_file_name': f'{get_schema_id("test_mysql_advanced")}_watermark.json'
            },
            {'name': 'test_jdbc_file_short_mysql'},
            {'name': 'test_jdbc_file_full_mysql'}, {'name': 'test_mysql_timezone_datetime'},
            {'name': 'test_mysql_no_schema'},
            {
                'name': 'test_watermark_local_timezone',
                'check_output_file_name': f'{get_schema_id("test_watermark_local_timezone")}_watermark.json'
            },
            {'name': 'test_jdbc_no_timestamp_condition'}
        ],
        'test_output': [
            {'name': 'test_mysql_no_schema', 'output': 'jdbc_file_full_no_schema.json', 'pipeline_type': 'mysql'},
        ],
        'test_output_schema': [
            {'name': 'test_mysql', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
            {'name': 'test_mysql_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
            {'name': 'test_mysql_timestamp_datetime', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
            {'name': 'test_mysql_timezone_datetime', 'output': 'jdbc_timezone.json', 'pipeline_type': 'mysql'},
            {'name': 'test_watermark_local_timezone', 'output': 'jdbc_timezone.json', 'pipeline_type': 'mysql'},
            {'name': 'test_mysql_advanced', 'output': 'jdbc_file_full.json', 'pipeline_type': 'mysql'},
        ],
        'test_delete_pipeline': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'},
                                 {'name': 'test_mysql_timestamp_datetime'},
                                 {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short_mysql'},
                                 {'name': 'test_jdbc_file_full_mysql'}, {'name': 'test_mysql_timezone_datetime'},
                                 {'name': 'test_mysql_no_schema'}, {'name': 'test_watermark_local_timezone'},
                                 {'name': 'test_jdbc_no_timestamp_condition'}],
        'test_source_delete': [{'name': 'test_jdbc'}, {'name': 'test_mysql_1'}]
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_watermark(self):
        schema_id = get_schema_id('test_mysql_advanced')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': 1512950400.0, 'schemaId': schema_id}
        schema_id = get_schema_id('test_watermark_local_timezone')
        # 1512943200 is 2 hours earlier than 1512950400
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': 1512943200.0, 'schemaId': schema_id}
