import pytest

from .test_zpipeline_base import TestPipelineBase, get_expected_schema_output
from ..conftest import get_output


class TestPromQL(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {
                'name': 'test_victoria'
            },
            {
                'name': 'test_victoria_2'
            },
            {
                'name': 'test_victoria_a'
            },
            {
                'name': 'test_thanos'
            },
            {
                'name': 'test_prometheus'
            },
            {
                'name': 'test_promql_schema'
            },
            {
                'name': 'test_promql_schema_rate'
            },
        ],
        'test_force_stop': [
            {
                'name': 'test_victoria'
            },
            {
                'name': 'test_victoria_2'
            },
            {
                'name': 'test_victoria_a'
            },
            {
                'name': 'test_thanos'
            },
            {
                'name': 'test_prometheus'
            },
            {
                'name': 'test_promql_schema'
            },
            {
                'name': 'test_promql_schema_rate'
            },
        ],
        'test_output': [
            {
                'name': 'test_victoria',
                'output': 'victoria.jsonl',
                'pipeline_type': 'victoria'
            },
            {
                'name': 'test_victoria_a',
                'output': 'victoria_advanced.jsonl',
                'pipeline_type': 'victoria'
            },
            {
                'name': 'test_thanos',
                'output': 'victoria.jsonl',
                'pipeline_type': 'thanos'
            },
            {
                'name': 'test_prometheus',
                'output': 'victoria.jsonl',
                'pipeline_type': 'prometheus'
            },
        ],
        'test_output_schema': [
            {
                'name': 'test_promql_schema',
                'output': 'victoria_schema.jsonl',
                'pipeline_type': 'victoria'
            },
            {
                'name': 'test_promql_schema_rate',
                'output': 'victoria_schema_rate.jsonl',
                'pipeline_type': 'victoria'
            },
        ],
        'test_delete_pipeline': [
            {
                'name': 'test_victoria'
            },
            {
                'name': 'test_victoria_2'
            },
            {
                'name': 'test_victoria_a'
            },
            {
                'name': 'test_thanos'
            },
            {
                'name': 'test_prometheus'
            },
            {
                'name': 'test_promql_schema'
            },
            {
                'name': 'test_promql_schema_rate'
            },
        ],
        'test_source_delete': [
            {
                'name': 'test_victoria'
            },
            {
                'name': 'test_victoria_2'
            },
            {
                'name': 'test_thanos'
            },
            {
                'name': 'test_prometheus'
            },
        ],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_start(self, cli_runner, name: str, sleep: int):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_output(self, name, pipeline_type, output):
        super().test_output(name, pipeline_type, output)

    def test_output_schema(self, name, pipeline_type, output):
        expected_output = get_expected_schema_output(name, output, pipeline_type)
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        if name == 'test_promql_schema_rate':
            # victoria returns aggregated values in random order
            expected_output.sort(key=compare)
            actual_output.sort(key=compare)
        assert actual_output == expected_output


def compare(obj):
    # instance is a dimensions that's present only in one metric so we sort by it
    if 'instance' in obj['dimensions']:
        return -1
    else:
        return 0
