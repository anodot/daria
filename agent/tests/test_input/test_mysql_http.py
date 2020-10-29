from datetime import datetime

from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.modules.streamsets_api_client import api_client
from agent import source


class TestMySQL:

    params = {
        'test_source_create': [{'name': 'test_jdbc', 'type': 'mysql', 'conn': 'mysql://root@mysql:3306/test'}],
        'test_create': [{'name': 'test_mysql', 'source': 'test_jdbc', 'timestamp_type': '', 'timestamp_name': 'timestamp_unix'},
                        {'name': 'test_mysql_timestamp_ms', 'source': 'test_jdbc', 'timestamp_type': 'unix_ms', 'timestamp_name': 'timestamp_unix_ms'},
                        {'name': 'test_mysql_timestamp_datetime', 'source': 'test_jdbc', 'timestamp_type': 'datetime', 'timestamp_name': 'timestamp_datetime'}],
        'test_create_timezone': [{'name': 'test_mysql_timezone_datetime', 'source': 'test_jdbc', 'timestamp_type': 'datetime', 'timezone': 'Europe/Berlin', 'timestamp_name': 'timestamp_datetime'}],
        'test_create_advanced': [{'name': 'test_mysql_advanced', 'source': 'test_jdbc'}],
    }

    def test_source_create(self, cli_runner, name, type, conn):
        result = cli_runner.invoke(source_cli.create, catch_exceptions=False, input=f"{type}\n{name}\n{conn}\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(pipeline_cli.create, catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n\n\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_timezone(self, cli_runner, name, source, timestamp_type, timestamp_name, timezone):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(pipeline_cli.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n{timezone}\n\nn\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n\nn\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_advanced(self, cli_runner, name, source):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(pipeline_cli.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}} AND country = \'USA\'\n86400\n{days_to_backfill}\n1\ntimestamp_unix\nunix\n\ny\ntest\nclicks:gauge impressions:gauge\nadsize country\nkey1:val1 key2:val2\n\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)
