import pytest
import requests
from .test_input.test_zpipeline_base import TestInputBase
from .test_pipelines.test_zpipeline_base import TestPipelineBase


class TestMonitoringMetrics(TestInputBase, TestPipelineBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [
            {'file_name': 'directory/sources'}
        ],
        'test_create_with_file': [
            {'file_name': 'directory/pipelines'}
        ],
        'test_start': [
            {'name': 'test_dir_csv'},
            {'name': 'test_dir_log'},
        ],
        'test_stop': [
            {'name': 'test_dir_csv'},
            {'name': 'test_dir_log'},
        ],
        'test_metric_pipeline_avg_lag': [
            {'name': 'test_dir_csv', 'metric_type': 'pipeline_avg_lag'},
            {'name': 'test_dir_log', 'metric_type': 'pipeline_avg_lag'}
        ]
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_stop(self, cli_runner, name):
        super().test_stop(cli_runner, name)

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_metric_pipeline_avg_lag(self, name, metric_type):
        url = "http://anodot-agent:80/metrics"
        response = requests.request("GET", url, headers={}, data={})
        metric_found = any(i.startswith(metric_type) and i.find(name) != -1 for i in response.text.split('\n'))
        assert metric_found

    def test_delete_pipeline(self, cli_runner, name=None):
        pytest.skip()

    def test_source_delete(self, cli_runner, name=None):
        pytest.skip()
