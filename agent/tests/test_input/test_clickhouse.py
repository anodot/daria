from datetime import datetime
from agent import source, cli
from .test_zpipeline_base import TestInputBase


class TestClickhouse(TestInputBase):
    __test__ = True
    params = {
        'test_source_create': [{'name': 'test_jdbc_clickhouse', 'type': 'clickhouse', 'conn': 'clickhouse://clickhouse:8123/test'}],
        'test_create': [
            {'name': 'test_clickhouse', 'source': 'test_jdbc_clickhouse', 'timestamp_type': '', 'timestamp_name': 'timestamp_unix'},
            {'name': 'test_clickhouse_timestamp_ms', 'source': 'test_jdbc_clickhouse', 'timestamp_type': 'unix_ms',
             'timestamp_name': 'timestamp_unix_ms'},
            {'name': 'test_clickhouse_timestamp_datetime', 'source': 'test_jdbc_clickhouse', 'timestamp_type': 'datetime',
             'timestamp_name': 'timestamp_datetime'}],
        'test_create_advanced': [{'name': 'test_clickhouse_advanced', 'source': 'test_jdbc_clickhouse'}],
        'test_create_with_file': [{'file_name': 'jdbc_pipelines_clickhouse'}],
        'test_create_source_with_file': [{'file_name': 'clickhouse_sources'}],
    }

    def test_source_create(self, cli_runner, name, type, conn):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"{type}\n{name}\n{conn}\n\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n')
        assert result.exit_code == 0

    def test_create_advanced(self, cli_runner, name, source):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}} AND country = \'USA\'\n\n86400\n{days_to_backfill}\n1\ntimestamp_unix\nunix\ny\ntest\nclicks:gauge impressions:gauge\nadsize country\nkey1:val1 key2:val2\n\n\n\n')
        assert result.exit_code == 0
