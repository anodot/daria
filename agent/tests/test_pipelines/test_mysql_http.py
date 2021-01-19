import pytest

from .test_zpipeline_base import TestPipelineBase, get_schema_id, get_expected_schema_output
from ..conftest import get_output


class TestMySQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_with_file': [{'file_name': 'jdbc_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'mysql_sources'}],
        'test_start': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'},
                       {'name': 'test_mysql_timestamp_datetime'},
                       {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'},
                       {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_reset': [{'name': 'test_mysql'}],
        'test_force_stop': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'},
                            {'name': 'test_mysql_timestamp_datetime'},
                            {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'},
                            {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_output': [{'name': 'test_mysql', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_datetime', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timezone_datetime', 'output': 'jdbc_timezone.json',
                         'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_advanced', 'output': 'jdbc_file_full.json', 'pipeline_type': 'mysql'}],
        'test_delete_pipeline': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'},
                                 {'name': 'test_mysql_timestamp_datetime'},
                                 {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'},
                                 {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_source_delete': [{'name': 'test_jdbc'}, {'name': 'test_mysql_1'}]
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
        expected_output = get_expected_schema_output(name, output, pipeline_type)
        assert get_output(f'{name}_{pipeline_type}.json') == expected_output

    def test_watermark(self):
        schema_id = get_schema_id('test_mysql_advanced')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': 1512885600, 'schemaId': schema_id}
