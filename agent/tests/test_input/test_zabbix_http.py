import sdc_client

from datetime import datetime
from agent import cli
from agent import source
from ..conftest import generate_input


class TestZabbix:
    def test_source_create(self, cli_runner):
        name = 'test_zabbix'
        input_ = {
            'type': 'zabbix',
            'name': name,
            'url': 'http://zabbix-web:8080',
            'user': 'Admin',
            'password': 'zabbix',
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner):
        name = 'test_zabbix'
        input_ = {
            'source': name,
            'name': name,
            'query file': 'tests/test_input/input_files/zabbix_query.json',
            'days to backfill': 0,
            'query interval': 86400,
            'data preview': 'n',
            'count': 'y',
            'counter name': 'counter',
            'value props': 'value:gauge',
            'measurement names': 'value:what',
            'dimensions': 'hosts/0/host content-provider service-provider',
            'delay': 0,
            'tags': 'test_type:zabbix',
            'preview': 'n',
        }
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert sdc_client.exists(name)

    def test_edit_advanced(self, cli_runner):
        days_to_backfill = (datetime.now() - datetime(year=2021, month=1, day=22)).days
        input_ = {
            'query file': '',
            'days to backfill': days_to_backfill,
            'query interval': '',
            'data preview': 'y',
            'count': '',
            'counter name': '',
            'value props': '',
            'measurement names': '',
            'dimensions': '',
            'delay': '',
            'transform file': '/home/zabbix_transform_value.csv',
            'static props': 'test_type:input',
            'tags': 'test:zabbix',
            'preview': 'n',
        }
        result = cli_runner.invoke(
            cli.pipeline.edit, ['test_zabbix', '-a'], catch_exceptions=False, input=generate_input(input_)
        )
        assert result.exit_code == 0
