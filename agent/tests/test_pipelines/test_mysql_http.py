import pytest

from ..fixtures import cli_runner
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestMySQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_with_file': [{'file_name': 'jdbc_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'mysql_sources'}],
        'test_start': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                       {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_reset': [{'name': 'test_mysql'}],
        'test_stop': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                      {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_output': [{'name': 'test_mysql', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_datetime', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timezone_datetime', 'output': 'jdbc_timezone.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_advanced', 'output': 'jdbc_file_full.json', 'pipeline_type': 'mysql'}],
        'test_delete_pipeline': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                                 {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}, {'name': 'test_mysql_timezone_datetime'}],
        'test_source_delete': [{'name': 'test_jdbc'}, {'name': 'test_mysql_1'}]
    }

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()
