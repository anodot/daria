from datetime import datetime
from agent import source, cli
from .test_zpipeline_base import TestInputBase
from ..conftest import generate_input


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
        input_ = {
            "type": type,
            "source name": name,
            "source connection string": conn,
            "username": "",
            "password": ""
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        input_ = {
            "source name": source,
            "pipeline name": name,
            "query": "SELECT * FROM test WHERE {TIMESTAMP_CONDITION}",
            "see preview": "",
            "interval": 86400,
            "days to backfill": days_to_backfill,
            "delay": 1,
            "timestamp name": timestamp_name,
            "timestamp_type": timestamp_type,
            "count records": "",
            "values": "clicks:gauge impressions:gauge",
            "dimensions": "adsize country",
            "static dimensions": "",
            "tags": "",
            "preview": ""
        }
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0

    def test_create_advanced(self, cli_runner, name, source):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        input_ = {
            "source name": source,
            "pipeline name": name,
            "query": "SELECT * FROM test WHERE {TIMESTAMP_CONDITION} AND country = 'USA'",
            "see preview": "",
            "interval": 86400,
            "days to backfill": days_to_backfill,
            "delay": 1,
            "timestamp name": "timestamp_unix",
            "timestamp_type": "unix",
            "count records": "y",
            "count records measurement name": "test",
            "values": "clicks:gauge impressions:gauge",
            "dimensions": "adsize country",
            "static dimensions": "key1:val1 key2:val2",
            "tags": "",
            "preview": ""
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
