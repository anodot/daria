import pytest

from .test_zpipeline_base import TestPipelineBase


class TestVictoria(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}, {'name': 'test_victoria_a'}],
        'test_force_stop': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}, {'name': 'test_victoria_a'}],
        'test_output': [
            {'name': 'test_victoria', 'output': 'victoria.jsonl', 'pipeline_type': 'victoria'},
            {'name': 'test_victoria_a', 'output': 'victoria_advanced.jsonl', 'pipeline_type': 'victoria'},
        ],
        'test_delete_pipeline': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}, {'name': 'test_victoria_a'}],
        'test_source_delete': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
