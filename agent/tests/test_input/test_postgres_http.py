from datetime import datetime
from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent import source
from agent.pipeline import streamsets


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
        result = cli_runner.invoke(source_cli.create, catch_exceptions=False,
                                   input=f"{type}\n{name}\n{conn}\npostgres\npassword\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(pipeline_cli.create, catch_exceptions=False,
                                   input=f'{source}\n{name}\ntest\n\n\n{days_to_backfill}\n\n\nclicks:gauge impressions:gauge\n{timestamp_name}\n{timestamp_type}\nadsize country\n\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_api_client_by_id(name).get_pipeline(name)

    def test_create_advanced(self, cli_runner, name, source):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(pipeline_cli.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\ntest\n\n\n{days_to_backfill}\n\ny\ntest\nclicks:gauge impressions:gauge\ntimestamp_unix\nunix\nadsize country\n\nkey1:val1 key2:val2\n\ncountry = \'USA\'\n\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_api_client_by_id(name).get_pipeline(name)
