import pytest

from agent import source
from .test_zpipeline_base import TestPipelineBase


class TestCacti(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'cacti'}],
        'test_force_stop': [{'name': 'cacti'}],
        'test_output': [
            {'name': 'cacti', 'output': 'cacti.json', 'pipeline_type': source.TYPE_CACTI},
        ],
        'test_delete_pipeline': [{'name': 'cacti'}],
        'test_source_delete': [{'name': 'cacti'}],
    }

    def test_create_source_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_create_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_start(self, cli_runner, name):
        super().test_start(cli_runner, name)

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
