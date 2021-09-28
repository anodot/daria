import pytest

from .zbase import PipelineBaseTest


class TestElastic(PipelineBaseTest):
    params = {
        'test_start': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                       {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_reset': [{'name': 'test_es_value_const'}],
        'test_stop': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                      {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_output': [{'name': 'test_es_value_const', 'output': 'json_value_const_adv.json',
                         'pipeline_type': 'elastic'},
                        {'name': 'test_es_timestamp_ms', 'output': 'json_value_property.json',
                         'pipeline_type': 'elastic'}],
        'test_delete_pipeline': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                                 {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_source_delete': [{'name': 'test_es'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
