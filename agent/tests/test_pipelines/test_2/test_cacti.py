import pytest

from agent import source
from ..test_zpipeline_base import TestPipelineBase, get_expected_output
from ...conftest import get_output


class TestCacti(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'cacti_archive'},
            {'name': 'cacti_dir'},
            {'name': 'cacti_dir_flex'},
            {'name': 'cacti_file'}
        ],
        'test_force_stop': [
            {'name': 'cacti_archive'},
            {'name': 'cacti_dir'},
            {'name': 'cacti_dir_flex'},
            {'name': 'cacti_file'}
        ],
        'test_output': [
            {'name': 'cacti_archive', 'output': 'cacti_archive.json', 'pipeline_type': source.TYPE_CACTI},
            {'name': 'cacti_dir', 'output': 'cacti_dir.json', 'pipeline_type': source.TYPE_CACTI},
            {'name': 'cacti_dir_flex', 'output': 'cacti_dir.json', 'pipeline_type': source.TYPE_CACTI},
            {'name': 'cacti_file', 'output': 'cacti_filtered.json', 'pipeline_type': source.TYPE_CACTI},
        ],
        'test_delete_pipeline': [
            {'name': 'cacti_archive'},
            {'name': 'cacti_dir'},
            {'name': 'cacti_dir_flex'},
            {'name': 'cacti_file'}
        ],
        'test_source_delete': [
            {'name': 'cacti_archive'},
            {'name': 'cacti_dir'}
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

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

    def test_output(self, name, pipeline_type, output):
        expected_output = get_expected_output(name, output, pipeline_type)
        self._wait(lambda: get_output(f'{name}_{pipeline_type}.json'))
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        if name in ['cacti_dir_flex']:
            expected_output = sorted(expected_output, key=lambda x: (x['timestamp'], x['value']))
            actual_output = sorted(actual_output, key=lambda x: (x['timestamp'], x['value']))
        assert actual_output == expected_output

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)
