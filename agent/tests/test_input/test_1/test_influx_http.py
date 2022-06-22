from agent import cli
from ..test_zpipeline_base import TestInputBase
from ...conftest import get_input_file_path


class TestInflux(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'influx_sources'}],
        'test_create_with_file': [{'file_name': 'influx_pipelines'}],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    def test_edit_with_file(self, cli_runner):
        input_file_path = get_input_file_path('influx_pipelines_edit.json')
        result = cli_runner.invoke(cli.pipeline.edit, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
