import os

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestPostgreSQL:

    params = {
        'test_source_create': [{'name': 'test_jdbc_postgres', 'type': 'postgres', 'conn': 'postgresql://postgres:5432/test'}],
        'test_create': [
            {'name': 'test_postgres', 'source': 'test_jdbc_postgres', 'timestamp_type': '', 'timestamp_name': 'timestamp_unix'},
            {'name': 'test_postgres_timestamp_ms', 'source': 'test_jdbc_postgres', 'timestamp_type': 'unix_ms',
             'timestamp_name': 'timestamp_unix_ms'},
            {'name': 'test_postgres_timestamp_datetime', 'source': 'test_jdbc_postgres', 'timestamp_type': 'datetime',
             'timestamp_name': 'timestamp_datetime'}],
        'test_create_advanced': [{'name': 'test_postgres_advanced', 'source': 'test_jdbc_postgres'}],
    }

    def test_source_create(self, cli_runner, name, type, conn):
        result = cli_runner.invoke(source_cli.create, input=f"{type}\n{name}\n{conn}\npostgres\npassword\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f'{source}\n{name}\ntest\n\n\n1000\n\n\nclicks:gauge impressions:gauge\n{timestamp_name}\n{timestamp_type}\nadsize country\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_advanced(self, cli_runner, name, source):
        result = cli_runner.invoke(pipeline_cli.create, ['-a'],
                                   input=f'{source}\n{name}\ntest\n\n\n1000\n\ny\nclicks:gauge impressions:gauge\ntimestamp_unix\nunix\nadsize country\n\nkey1:val1 key2:val2\n\ncountry = \'USA\'\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)
