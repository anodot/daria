import pytest
import requests

from .test_input.test_zpipeline_base import TestInputBase
from .test_pipelines.test_zpipeline_base import TestPipelineBase


class TestMonitoringMetrics(TestInputBase, TestPipelineBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [
            {'file_name': 'monitoring/sources'}
        ],
        'test_create_with_file': [
            {'file_name': 'monitoring/pipelines'}
        ],
        'test_start': [
            {'name': 'test_dir_monitoring_csv'},
        ],
        'test_stop': [
            {'name': 'test_dir_monitoring_csv'},
        ],
        'test_monitoring_metrics': [
            {'name': 'test_dir_monitoring_csv', 'metric_type': 'pipeline_avg_lag_seconds'},
            {'name': 'test_dir_monitoring_csv', 'metric_type': 'watermark_delta'},
            {'name': 'test_dir_monitoring_csv', 'metric_type': 'watermark_sent_total'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_dir_monitoring_csv'},
        ],
        'test_source_delete': [
            {'name': 'test_dir_monitoring_csv'},
        ],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_stop(self, cli_runner, name, check_output_file_name):
        super().test_stop(cli_runner, name, check_output_file_name)

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_monitoring_metrics(self, name, metric_type):
        response = requests.get('http://localhost/metrics')
        assert response.status_code == 200
        metrics = response.json()
        metric_found = any(i['properties'].get('pipeline_id') == name and i['properties']['what'] == metric_type for i in metrics)
        assert metric_found
