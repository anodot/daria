import pytest

from agent import source
from .base import PipelineBaseTest


class TestSolarWinds(PipelineBaseTest):
    params = {
        'test_start': [{'name': 'solarwinds'}, {'name': 'solarwinds_file'}],
        'test_force_stop': [{'name': 'solarwinds'}, {'name': 'solarwinds_file'}],
        'test_output': [
            {'name': 'solarwinds', 'output': 'solarwinds.json', 'pipeline_type': source.TYPE_SOLARWINDS},
        ],
        'test_delete_pipeline': [{'name': 'solarwinds'}, {'name': 'solarwinds_file'}],
        'test_source_delete': [{'name': 'solarwinds'}, {'name': 'solarwinds_file'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_watermark(self):
        pytest.skip()

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
