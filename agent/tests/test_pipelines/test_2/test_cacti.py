import pytest
import time

from agent import source
from ..test_zpipeline_base import TestPipelineBase


class TestCacti(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'cacti_archive'}, {'name': 'cacti_dir'}, {'name': 'cacti_file', 'sleep': 15}],
        'test_force_stop': [{'name': 'cacti_archive'}, {'name': 'cacti_dir'}, {'name': 'cacti_file'}],
        'test_output': [
            {'name': 'cacti_archive', 'output': 'cacti_archive.json', 'pipeline_type': source.TYPE_CACTI},
            {'name': 'cacti_dir', 'output': 'cacti_dir.json', 'pipeline_type': source.TYPE_CACTI},
            {'name': 'cacti_file', 'output': 'cacti_filtered.json', 'pipeline_type': source.TYPE_CACTI},
        ],
        'test_delete_pipeline': [{'name': 'cacti_archive'}, {'name': 'cacti_dir'}, {'name': 'cacti_file'}],
        'test_source_delete': [{'name': 'cacti_archive'}, {'name': 'cacti_dir'}, {'name': 'cacti_file'}],
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

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
