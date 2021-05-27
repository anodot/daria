from agent import cli
from agent import source
from .test_zpipeline_base import TestInputBase
from ..conftest import get_input_file_path


class TestInflux(TestInputBase):
    __test__ = True
    params = {
        'test_source_create': [{'name': 'test_influx', 'offset': '10/03/2019 12:53'},
                               {'name': 'test_influx_offset', 'offset': '19/03/2019 12:53'}],
        'test_create': [{'name': 'test_basic', 'source_': 'test_influx'},
                        {'name': 'test_basic_offset', 'source_': 'test_influx_offset'}],
        'test_create_with_file': [{'file_name': 'influx_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'influx_sources'}],
    }

    def test_source_create(self, cli_runner, name, offset):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"influx\n{name}\nhttp://influx:8086\nadmin\nadmin\ntest\n{offset}\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source_):
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source_}\n{name}\ncpu_test\n\nusage_active:gauge usage_idle:gauge\ncpu zone host\n\n1200000\n\n')
        assert result.exit_code == 0

    def test_create_adv(self, cli_runner):
        pipeline_id = 'test_influx_adv'
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f"test_influx\n{pipeline_id}\ncpu_test\n\nusage_active:gauge usage_idle:gauge\ncpu zone host\n \nkey:val key1:val1\nkey:val key1:val1\n\n1200000\nzone = 'GEO'\nn\n\n")
        assert result.exit_code == 0

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_edit_with_file(self, cli_runner):
        input_file_path = get_input_file_path('influx_pipelines_edit.json')
        result = cli_runner.invoke(cli.pipeline.edit, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
