import pytest

from ..fixtures import cli_runner
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestInflux(TestPipelineBase):
    __test__ = True

    params = {
        'test_create_with_file': [{'file_name': 'influx_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'influx_sources'}],
        'test_edit_with_file': [{'file_name': 'influx_pipelines_edit'}],
        'test_start': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                       {'name': 'test_influx_file_full'}, {'name': 'test_influx_adv'}],
        'test_stop': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                      {'name': 'test_influx_file_full'}, {'name': 'test_influx_adv'}],
        'test_reset': [{'name': 'test_basic'}],
        'test_output': [{'name': 'test_basic', 'output': 'influx.json', 'pipeline_type': 'influx'},
                        {'name': 'test_basic_offset', 'output': 'influx_offset.json', 'pipeline_type': 'influx'},
                        {'name': 'test_influx_file_short', 'output': 'influx.json', 'pipeline_type': 'influx'},
                        {'name': 'test_influx_file_full', 'output': 'influx_file_full.json', 'pipeline_type': 'influx'},
                        {'name': 'test_influx_adv', 'output': 'influx_adv.json', 'pipeline_type': 'influx'}],
        'test_delete_pipeline': [{'name': 'test_basic'}, {'name': 'test_basic_offset'},
                                 {'name': 'test_influx_file_short'}, {'name': 'test_influx_file_full'},
                                 {'name': 'test_influx_adv'}],
        'test_source_delete': [{'name': 'test_influx'}, {'name': 'test_influx_offset'}, {'name': 'test_influx_1'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()
