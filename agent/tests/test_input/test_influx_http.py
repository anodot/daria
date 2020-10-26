from agent import cli
from agent import source
from agent.pipeline import streamsets


class TestInflux:

    params = {
        'test_source_create': [{'name': 'test_influx', 'offset': '10/03/2019 12:53'},
                               {'name': 'test_influx_offset', 'offset': '19/03/2019 12:53'}],
        'test_create': [{'name': 'test_basic', 'source_': 'test_influx'},
                        {'name': 'test_basic_offset', 'source_': 'test_influx_offset'}],
    }

    def test_source_create(self, cli_runner, name, offset):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"influx\n{name}\nhttp://influx:8086\nadmin\nadmin\ntest\n{offset}\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source_):
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source_}\n{name}\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n\n1200000\n\n\n')
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_create_adv(self, cli_runner):
        pipeline_id = 'test_influx_adv'
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f"test_influx\n{pipeline_id}\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n \nkey:val key1:val1\nkey:val key1:val1\n\n1200000\nzone = 'GEO'\n\n\n")
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline('test_influx_adv')
