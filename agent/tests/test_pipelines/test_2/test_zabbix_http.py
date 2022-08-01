import pytest

from ..test_zpipeline_base import TestPipelineBase, get_expected_output
from ...conftest import get_output


class TestZabbix(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_force_stop': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_output': [
            {'name': 'test_zabbix', 'output': 'zabbix.json', 'pipeline_type': 'zabbix'},
            {'name': 'test_zabbix_edit_query', 'output': 'zabbix2.json', 'pipeline_type': 'zabbix'},
        ],
        'test_delete_pipeline': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_source_delete': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_output(self, name, pipeline_type, output):
        super().test_output(name, pipeline_type, output)
