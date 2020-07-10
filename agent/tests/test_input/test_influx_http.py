import os

from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.streamsets_api_client import api_client
from ...source import source_repository


class TestInflux:

    params = {
        'test_source_create': [{'name': 'test_influx', 'offset': '10/03/2019 12:53'},
                               {'name': 'test_influx_offset', 'offset': '19/03/2019 12:53'}],
        'test_create': [{'name': 'test_basic', 'source': 'test_influx'},
                        {'name': 'test_basic_offset', 'source': 'test_influx_offset'}],
    }

    def test_source_create(self, cli_runner, name, offset):
        result = cli_runner.invoke(source_cli.create, input=f"influx\n{name}\nhttp://influx:8086\nadmin\nadmin\ntest\n{offset}\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source_repository.SOURCE_DIRECTORY, f'{name}.json'))

    def test_create(self, cli_runner, name, source):
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f'{source}\n{name}\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n\n7000000\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_adv(self, cli_runner):
        result = cli_runner.invoke(pipeline_cli.create, ['-a'],
                                   input="test_influx\ntest_influx_adv\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n \nkey:val key1:val1\nkey:val key1:val1\n\n7000000\nzone = 'GEO'\n\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline('test_influx_adv')
