import pytest

from .test_zpipeline_base import TestPipelineBase, get_expected_output
from ..conftest import get_output


class TestTopology(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'topology_site', 'sleep': 30},
            {'name': 'topology_region', 'sleep': 30},
        ],
        'test_force_stop': [
            {'name': 'topology_site'},
            {'name': 'topology_region'},
        ],
        'test_output': [
            {'name': 'topology', 'output_file': 'topology_site.json', 'pipeline_type': 'SITE'},
            {'name': 'topology', 'output_file': 'topology_province.json', 'pipeline_type': 'PROVINCE'},
        ],
        'test_delete_pipeline': [
            {'name': 'topology_site'},
            {'name': 'topology_region'},
        ],
        'test_source_delete': [
            {'name': 'topology_site_source'},
            {'name': 'topology_region_source'},
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

    def test_output(self, name, pipeline_type, output_file):
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        expected_output = get_expected_output(name, output_file)
        for obj in actual_output:
            obj.pop('timestamp')
        assert actual_output == expected_output
