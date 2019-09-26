import os
import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_pipeline_base import TestPipelineBase, pytest_generate_tests


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
        'test_stop': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                      {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}],
        'test_output': [{'name': 'test_mysql', 'output': 'jdbc.json'},
                        {'name': 'test_mysql_timestamp_ms', 'output': 'jdbc.json'},
                        {'name': 'test_mysql_timestamp_datetime', 'output': 'jdbc.json'},
                        {'name': 'test_mysql_advanced', 'output': 'jdbc_file_full.json'},
                        {'name': 'test_jdbc_file_short', 'output': 'jdbc.json'},
                        {'name': 'test_jdbc_file_full', 'output': 'jdbc_file_full.json'}],
        'test_delete_pipeline': [{'name': 'test_mysql'}, {'name': 'test_mysql_timestamp_ms'}, {'name': 'test_mysql_timestamp_datetime'},
                                 {'name': 'test_mysql_advanced'}, {'name': 'test_jdbc_file_short'}, {'name': 'test_jdbc_file_full'}],
        'test_source_delete': [{'name': 'test_jdbc'}]
    }

    def test_source_create(self, cli_runner, name, type, conn):
        result = cli_runner.invoke(source_cli.create, input=f"{type}\n{name}\n{conn}\n\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f'{source}\n{name}\ntest\n\nclicks:gauge impressions:gauge\n{timestamp_name}\n{timestamp_type}\nadsize country\n\n\n1000\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_advanced(self, cli_runner, name, source):
        result = cli_runner.invoke(pipeline_cli.create, ['-a'],
                                   input=f'{source}\n{name}\ntest\ny\nclicks:gauge impressions:gauge\ntimestamp_unix\nunix\nadsize country\nkey1:val1 key2:val2\n\n\n1000\ncountry = \'USA\'\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
