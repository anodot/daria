import pytest

from agent import source
from .test_zpipeline_base import TestPipelineBase, get_expected_output
from ..conftest import get_output


class TestTopology(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {
                'name': 'topology'
            },
        ],
        'test_force_stop': [
            {
                'name': 'topology'
            },
        ],
        'test_output': [
            {
                'name': 'topology',
                'output': 'topology.json',
                'pipeline_type': source.TYPE_TOPOLOGY
            },
        ],
        'test_delete_pipeline': [
            {
                'name': 'topology'
            },
        ],
        'test_source_delete': [
            {
                'name': 'topology'
            },
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

    def test_output(self, name, pipeline_type, output):
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        expected_output = get_expected_output(name, output, pipeline_type)
        for obj in actual_output:
            obj.pop('timestamp')
        assert actual_output == expected_output
