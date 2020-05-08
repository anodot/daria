import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestMongo(TestPipelineBase):
    __test__ = True
    params = {
        'test_create': [{'name': 'test_value_const', 'options': ['-a'], 'value': '2\nconstant\ncounter', 'timestamp': 'timestamp_unix', 'timestamp_type': 'unix', 'properties': 'key1:val1\n'},
                        {'name': 'test_timestamp_ms', 'options': [], 'value': 'Clicks\nproperty\ngauge', 'timestamp': 'timestamp_unix_ms', 'timestamp_type': 'unix_ms', 'properties': ''},
                        {'name': 'test_timestamp_datetime', 'options': [], 'value': 'Clicks\n', 'timestamp': 'timestamp_datetime', 'timestamp_type': 'datetime', 'properties': ''},
                        {'name': 'test_timestamp_id', 'options': [], 'value': 'Clicks\n', 'timestamp': '_id', 'timestamp_type': 'unix', 'properties': 'key1:val1'},
                        {'name': 'test_timestamp_string', 'options': ['-a'], 'value': 'Clicks\nconstant\n', 'timestamp': 'timestamp_string', 'timestamp_type': 'string\nM/d/yyyy H:mm:ss', 'properties': 'key1:val1\n'}],
        'test_create_with_file': [{'file_name': 'mongo_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'mongo_sources'}],
        'test_edit': [{'options': ['test_value_const'], 'value': '1\n\n'},
                      {'options': ['test_timestamp_string', '-a'], 'value': 'Clicks\nproperty'}],
        'test_start': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_reset': [{'name': 'test_value_const'}],
        'test_stop': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_output': [{'name': 'test_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_ms', 'output': 'json_value_property.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_string', 'output': 'json_value_property_adv.json', 'pipeline_type': 'mongo'},
                        {'name': 'test_timestamp_datetime', 'output': 'json_value_property.json', 'pipeline_type': 'mongo'}],
        'test_delete_pipeline': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_source_delete': [{'name': 'test_mongo'}, {'name': 'test_mongo_1'}],
        'test_output_exists': [{'name': 'test_timestamp_id', 'pipeline_type': 'mongo'}]
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()
