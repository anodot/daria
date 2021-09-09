import pytest

from .test_zpipeline_base import TestPipelineBase, get_schema_id
from ..conftest import get_output


class TestObservium(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'observium'}],
        'test_force_stop': [{'name': 'observium'}],
        'test_output_schema': [
            {'name': 'observium', 'output': 'observium_schema.json', 'pipeline_type': 'observium'},
        ],
        'test_delete_pipeline': [{'name': 'observium'}],
        'test_source_delete': [{'name': 'observium'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_watermark(self, name):
        schema_id = get_schema_id(name)
        watermark = get_output(f'{schema_id}_watermark.json')
        assert schema_id == watermark['schemaId']
