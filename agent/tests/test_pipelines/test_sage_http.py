import pytest

from .test_zpipeline_base import TestPipelineBase


class TestSage(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps'},
        ],
        'test_force_stop': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps'},
        ],
        'test_reset': [
            {'name': 'test_sage_value_const'},
        ],
        'test_output': [
            {'name': 'test_sage_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'sage'},
            {'name': 'test_sage', 'output': 'json_value_property.json', 'pipeline_type': 'sage'},
        ],
        'test_output_schema': [
            {'name': 'test_sage_schema_file', 'output': 'sage_file_schema.json', 'pipeline_type': 'sage'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps'},
        ],
        'test_source_delete': [
            {'name': 'test_sage'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()
