import pytest

from agent import source
from .test_zpipeline_base import TestPipelineBase


class TestRRD(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'rrd'},
        ],
        'test_force_stop': [
            {'name': 'rrd'},
        ],
        'test_output': [
            {'name': 'rrd', 'output': 'rrd_dir.json', 'pipeline_type': source.TYPE_RRD},
        ],
        'test_delete_pipeline': [
            {'name': 'rrd'},
        ],
        'test_source_delete': [
            {'name': 'rrd'},
        ],
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

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)
