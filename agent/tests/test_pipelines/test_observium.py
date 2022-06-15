import pytest

from .test_zpipeline_base import TestPipelineBase


class TestObservium(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {
                'name': 'observium_ports',
            },
            {
                'name': 'observium_mempools',
            },
            {
                'name': 'observium_mempools_edit',
            },
            {
                'name': 'observium_processors',
            },
            {
                'name': 'observium_storage',
                'sleep': 40
            },
            {
                'name': 'observium_storage_transform',
                'sleep': 40
            },
        ],
        'test_force_stop': [
            {
                'name': 'observium_ports'
            },
            {
                'name': 'observium_mempools'
            },
            {
                'name': 'observium_mempools_edit'
            },
            {
                'name': 'observium_processors'
            },
            {
                'name': 'observium_storage'
            },
            {
                'name': 'observium_storage_transform'
            },
        ],
        'test_output_schema': [
            {
                'name': 'observium_ports',
                'output': 'observium_ports_schema.json',
                'pipeline_type': 'observium'
            },
            {
                'name': 'observium_mempools',
                'output': 'observium_mempools_schema.json',
                'pipeline_type': 'observium'
            },
            {
                'name': 'observium_mempools_edit',
                'output': 'observium_mempools_schema_edit.json',
                'pipeline_type': 'observium'
            },
            {
                'name': 'observium_processors',
                'output': 'observium_processors_schema.json',
                'pipeline_type': 'observium'
            },
            {
                'name': 'observium_storage',
                'output': 'observium_storage_schema.json',
                'pipeline_type': 'observium'
            },
            {
                'name': 'observium_storage_transform',
                'output': 'observium_storage_transform.json',
                'pipeline_type': 'observium'
            },
        ],
        'test_watermark': [
            {
                'name': 'observium_ports',
                'timestamp': 1628160620
            },
            {
                'name': 'observium_mempools',
                'timestamp': 1628160603
            },
            {
                'name': 'observium_mempools_edit',
                'timestamp': 1628160603
            },
            {
                'name': 'observium_processors',
                'timestamp': 1633517705
            },
            {
                'name': 'observium_storage',
                'timestamp': 1633518002
            },
            {
                'name': 'observium_storage_transform',
                'timestamp': 1633518002
            },
        ],
        'test_delete_pipeline': [
            {
                'name': 'observium_ports'
            },
            {
                'name': 'observium_mempools'
            },
            {
                'name': 'observium_mempools_edit'
            },
            {
                'name': 'observium_processors'
            },
            {
                'name': 'observium_storage'
            },
            {
                'name': 'observium_storage_transform'
            },
        ],
        'test_source_delete': [
            {
                'name': 'observium'
            },
        ],
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
