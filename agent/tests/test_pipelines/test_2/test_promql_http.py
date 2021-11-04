import pytest

from ..test_zpipeline_base import TestPipelineBase


class TestPromQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_victoria'},
            {'name': 'test_victoria_2'},
            {'name': 'test_victoria_a'},
            {'name': 'test_thanos'},
            {'name': 'test_prometheus'},
        ],
        'test_force_stop': [
            {'name': 'test_victoria'},
            {'name': 'test_victoria_2'},
            {'name': 'test_victoria_a'},
            {'name': 'test_thanos'},
            {'name': 'test_prometheus'},
        ],
        'test_output': [
            {'name': 'test_victoria', 'output': 'victoria.jsonl', 'pipeline_type': 'victoria'},
            {'name': 'test_victoria_a', 'output': 'victoria_advanced.jsonl', 'pipeline_type': 'victoria'},
            {'name': 'test_thanos', 'output': 'victoria.jsonl', 'pipeline_type': 'thanos'},
            {'name': 'test_prometheus', 'output': 'victoria.jsonl', 'pipeline_type': 'prometheus'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_victoria'},
            {'name': 'test_victoria_2'},
            {'name': 'test_victoria_a'},
            {'name': 'test_thanos'},
            {'name': 'test_prometheus'},
        ],
        'test_source_delete': [
            {'name': 'test_victoria'},
            {'name': 'test_victoria_2'},
            {'name': 'test_thanos'},
            {'name': 'test_prometheus'},
        ],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
