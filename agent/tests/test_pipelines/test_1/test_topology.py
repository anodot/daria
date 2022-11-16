import pytest

from ..test_zpipeline_base import TestPipelineBase, get_expected_output
from ...conftest import get_output, Order


class TestTopology(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'topology_site'},
            {'name': 'topology_region'},
        ],
        'test_force_stop': [
            {'name': 'topology_site', 'check_output_file_name': 'topology_SITE.json'},
            {'name': 'topology_region', 'check_output_file_name': 'topology_REGION.json'},
        ],
        'test_output': [
            {'name': 'topology', 'output_file': 'topology_site.json', 'pipeline_type': 'SITE'},
            {'name': 'topology', 'output_file': 'topology_region.json', 'pipeline_type': 'REGION'},
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

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_watermark(self):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_output(self, name, pipeline_type, output_file):
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        expected_output = get_expected_output(name, output_file)
        for obj in actual_output:
            obj.pop('timestamp')
        assert actual_output == expected_output
