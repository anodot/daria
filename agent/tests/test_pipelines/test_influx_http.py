import os
import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_pipeline_base import TestPipelineBase, pytest_generate_tests
from agent.pipeline.config_handlers.influx import InfluxConfigHandler


@pytest.fixture(autouse=True)
def pipeline_id(monkeypatch):
    def constant_pipeline_id(self):
        return 'pipeline_id'
    monkeypatch.setattr(InfluxConfigHandler, 'get_pipeline_id', constant_pipeline_id)


@pytest.fixture(autouse=True)
def pipeline_type(monkeypatch):
    def constant_pipeline_type(self):
        return 'type'
    monkeypatch.setattr(InfluxConfigHandler, 'get_pipeline_type', constant_pipeline_type)


class TestInflux(TestPipelineBase):
    __test__ = True

    params = {
        'test_source_create': [{'name': 'test_influx', 'offset': '10/03/2019 12:53'},
                               {'name': 'test_influx_offset', 'offset': '19/03/2019 12:53'}],
        'test_create': [{'name': 'test_basic', 'source': 'test_influx'},
                        {'name': 'test_basic_offset', 'source': 'test_influx_offset'}],
        'test_create_with_file': [{'file_name': 'influx_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'influx_sources'}],
        'test_edit_with_file': [{'file_name': 'influx_pipelines_edit'}],
        'test_start': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                       {'name': 'test_influx_file_full'}],
        'test_stop': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                      {'name': 'test_influx_file_full'}],
        'test_output': [{'name': 'test_basic', 'output': 'influx.json'},
                        {'name': 'test_basic_offset', 'output': 'influx_offset.json'},
                        {'name': 'test_influx_file_short', 'output': 'influx.json'},
                        {'name': 'test_influx_file_full', 'output': 'influx_file_full.json'}],
        'test_delete_pipeline': [{'name': 'test_basic'}, {'name': 'test_basic_offset'},
                                 {'name': 'test_influx_file_short'}, {'name': 'test_influx_file_full'}],
        'test_source_delete': [{'name': 'test_influx'}, {'name': 'test_influx_offset'}, {'name': 'test_influx_1'}],
    }

    def test_source_create(self, cli_runner, name, offset):
        result = cli_runner.invoke(source_cli.create, input=f"influx\n{name}\nhttp://influx:8086\nadmin\nadmin\ntest\n{offset}\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

    def test_create(self, cli_runner, name, source):
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f'{source}\n{name}\ncpu_test\n\nusage_active usage_idle\n\ncpu zone host\n\n7000000\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()