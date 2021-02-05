import pytest

from .test_zpipeline_base import TestPipelineBase


class TestZabbix(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'zabbix_sources'}],
        'test_create_with_file': [{'file_name': 'zabbix_pipelines'}],
        'test_start': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
        'test_force_stop': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
        'test_output': [
            {'name': 'test_zabbix', 'output': 'zabbix.json', 'pipeline_type': 'zabbix'},
        ],
        'test_delete_pipeline': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
        'test_source_delete': [{'name': 'test_zabbix'}, {'name': 'test_zabbix_file'}],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()
