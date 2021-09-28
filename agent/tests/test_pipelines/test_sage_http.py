import pytest

from .zbase import PipelineBaseTest


class TestSage(PipelineBaseTest):
    params = {
        'test_start': [{'name': 'test_sage_value_const'}, {'name': 'test_sage'}, {'name': 'test_sage_file'}],
        'test_force_stop': [{'name': 'test_sage_value_const'}, {'name': 'test_sage'}, {'name': 'test_sage_file'}],
        'test_reset': [{'name': 'test_sage_value_const'}],
        'test_output': [{'name': 'test_sage_value_const', 'output': 'json_value_const_adv.json',
                         'pipeline_type': 'sage'},
                        {'name': 'test_sage', 'output': 'json_value_property.json',
                         'pipeline_type': 'sage'}
                        ],
        'test_delete_pipeline': [{'name': 'test_sage_value_const'}, {'name': 'test_sage'}, {'name': 'test_sage_file'}],
        'test_source_delete': [{'name': 'test_sage'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
