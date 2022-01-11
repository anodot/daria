import pytest

from .test_zpipeline_base import TestPipelineBase


class TestMongo(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_reset': [{'name': 'test_value_const'}],
        'test_stop': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                      {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_output': [{'name': 'test_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_ms', 'output': 'json_value_property.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_string', 'output': 'json_value_property_adv.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_datetime', 'output': 'json_value_property.json', 'pipeline_type': 'mongo'}],
        'test_delete_pipeline': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                                 {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_source_delete': [{'name': 'test_mongo'}, {'name': 'test_mongo_1'}, {'name': 'test_mongo_encrypted_pass'}]
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()
