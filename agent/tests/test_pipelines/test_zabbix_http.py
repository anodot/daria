import pytest

from .test_zpipeline_base import TestPipelineBase


class TestZabbix(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_force_stop': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_output': [
            {'name': 'test_zabbix', 'output': 'zabbix.json', 'pipeline_type': 'zabbix'},
            {'name': 'test_zabbix_edit_query', 'output': 'zabbix.json', 'pipeline_type': 'zabbix'},
        ],
        'test_delete_pipeline': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}, {'name': 'test_zabbix_edit_query'}],
        'test_source_delete': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
