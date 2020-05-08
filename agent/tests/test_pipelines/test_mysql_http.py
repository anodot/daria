import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestMySQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_source_create': [{'name': 'test_jdbc', 'type': 'mysql', 'conn': 'mysql://root@mysql:3306/test'}],
        'test_create': [{'name': 'test_mysql', 'source': 'test_jdbc', 'timestamp_type': '', 'timestamp_name': 'timestamp_unix'},
                        {'name': 'test_mysql_timestamp_ms', 'source': 'test_jdbc', 'timestamp_type': 'unix_ms', 'timestamp_name': 'timestamp_unix_ms'},
                        {'name': 'test_mysql_timestamp_datetime', 'source': 'test_jdbc', 'timestamp_type': 'datetime', 'timestamp_name': 'timestamp_datetime'}],
        'test_create_advanced': [{'name': 'test_mysql_advanced', 'source': 'test_jdbc'}],
        'test_create_with_file': [{'file_name': 'jdbc_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'mysql_sources'}],
        'test_start': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                       {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}],
        'test_reset': [{'name': 'test_mysql'}],
        'test_stop': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                      {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}],
        'test_output': [{'name': 'test_mysql', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_ms', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_timestamp_datetime', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_mysql_advanced', 'output': 'jdbc_file_full.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_jdbc_file_short', 'output': 'jdbc.json', 'pipeline_type': 'mysql'},
                        {'name': 'test_jdbc_file_full', 'output': 'jdbc_file_full.json', 'pipeline_type': 'mysql'}],
        'test_delete_pipeline': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                                 {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}],
        'test_source_delete': [{'name': 'test_jdbc'}, {'name': 'test_mysql_1'}]
    }

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
