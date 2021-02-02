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
            'query file': 'query.json',
            'count': 'n',
            'value props': 'value:gauge',
            'measurement names': 'value:name',
            'dimensions': 'name hostid',
            'query interval': 86400,
            'collect since': 0,
            'delay': 0,
            'tags': 'test_type:zabbix',
            'preview': 'n',
        }
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert sdc_client.exists(name)

    def test_edit(self, cli_runner):
        days_to_backfill = (datetime.now() - datetime(year=2021, month=1, day=22)).days
        input_ = {
            'query file': '',
            'count': '',
            'value props': '',
            'measurement names': '',
            'dimensions': '',
            'query interval': '',
            'collect since': days_to_backfill,
            'delay': '',
            'preview': 'n',
        }
        result = cli_runner.invoke(
            cli.pipeline.edit, ['test_zabbix'], catch_exceptions=False, input=generate_input(input_)
        )
        assert result.exit_code == 0
