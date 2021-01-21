from datetime import datetime
from agent import source, streamsets, cli
from ..conftest import generate_input

days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1


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
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=f"{type}\n{name}\n{conn}\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_create_timezone(self, cli_runner, name, source, timestamp_type, timestamp_name, timezone):
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n{timezone}\nn\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n\nn\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_create_advanced(self, cli_runner, name, source):
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}} AND country = \'USA\'\n\n86400\n{days_to_backfill}\n1\ntimestamp_unix\nunix\ny\ntest\nclicks:gauge impressions:gauge\nadsize country\nkey1:val1 key2:val2\n\n\n\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_create_advanced_no_schema(self, cli_runner):
        pipeline_id = 'test_mysql_no_schema'
        input_ = {
            'source': 'test_jdbc',
            'pipeline id': pipeline_id,
            'query': "SELECT * FROM test WHERE {TIMESTAMP_CONDITION} AND country = 'USA'",
            'data preview': 'y',
            'query interval': 86400,
            'collect since': 0,
            'delay': 1,
            'timestamp column': 'timestamp_unix',
            'timestamp type': 'unix',
            'count records': 'y',
            'measurement name': 'test',
            'value columns': 'clicks:gauge impressions:gauge',
            'dimensions': 'adsize country',
            'additional properties': 'key1:val1 key2:val2',
            'tags': '',
            'use schema': 'n',
            'show preview': 'n',
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(pipeline_id)

    def test_edit_advanced_no_schema(self, cli_runner):
        pipeline_id = 'test_mysql_no_schema'
        input_ = {
            'query': "",
            'preview': 'n',
            'query interval': '',
            'collect since': days_to_backfill,
            'delay': '',
            'timestamp column': '',
            'timestamp type': '',
            'count records': '',
            'measurement name': '',
            'value columns': '',
            'dimensions': '',
            'use schema': '',
            'show preview': 'n'
        }
        result = cli_runner.invoke(cli.pipeline.edit, [pipeline_id], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(pipeline_id)
