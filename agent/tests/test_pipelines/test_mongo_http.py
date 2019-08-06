import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination, get_input_file_path
from agent.pipeline import cli as pipeline_cli, Pipeline
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_pipeline import TestPipeline, pytest_generate_tests


class TestMongo(TestPipeline):
    __test__ = True
    params = {
        'test_create': [{'name': 'test_value_const', 'options': ['-a'], 'value': '2\nconstant', 'timestamp': 'timestamp_unix', 'timestamp_type': 'unix', 'properties': ''},
                        {'name': 'test_timestamp_ms', 'options': [], 'value': 'Clicks\nproperty', 'timestamp': 'timestamp_unix_ms', 'timestamp_type': 'unix_ms', 'properties': 'key1:val1'},
                        {'name': 'test_timestamp_datetime', 'options': [], 'value': 'Clicks', 'timestamp': 'timestamp_datetime', 'timestamp_type': 'unix', 'properties': ''},
                        {'name': 'test_timestamp_id', 'options': [], 'value': 'Clicks', 'timestamp': '_id', 'timestamp_type': 'datetime', 'properties': 'key1:val1'},
                        {'name': 'test_timestamp_string', 'options': ['-a'], 'value': 'Clicks\nconstant', 'timestamp': 'timestamp_string', 'timestamp_type': 'string\nM/d/yyyy H:mm:ss', 'properties': 'key1:val1'}],
        'test_create_with_file': [{'file_name': 'mongo_pipelines'}],
        'test_edit': [{'options': ['test_value_const'], 'value': '1\n\n'},
                      {'options': ['test_timestamp_string', '-a'], 'value': 'Clicks\nproperty'}],
        'test_start': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_stop': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_output': [{'name': 'test_value_const', 'output': 'json_value_const_adv.json'},
                        {'name': 'test_timestamp_ms', 'output': 'json_value_property.json'},
                        {'name': 'test_timestamp_string', 'output': 'json_value_property_adv.json'},
                        {'name': 'test_timestamp_datetime', 'output': 'json_value_property.json'}],
        'test_delete_pipeline': [{'name': 'test_value_const'}, {'name': 'test_timestamp_ms'},
                       {'name': 'test_timestamp_string'}, {'name': 'test_timestamp_datetime'},
                       {'name': 'test_timestamp_id'}, {'name': 'test_mongo_file_short'},
                       {'name': 'test_mongo_file_full'}],
        'test_source_delete': [{'name': 'test_mongo'}],
        'test_output_exists': [{'name': 'test_timestamp_id'}]
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input="""mongo\ntest_mongo\nmongodb://mongo:27017\nroot\nroot\nadmin\ntest\nadtec\n\n\n2015-01-01 00:00:00\n\n\n\n""")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_mongo.json'))

    def test_source_edit(self, cli_runner):
        result = cli_runner.invoke(source_cli.edit, ['test_mongo'], input="""\n\n\n\n\nadtech\n\n\n\n\n\n\n""")
        with open(os.path.join(Source.DIR, 'test_mongo.json'), 'r') as f:
            source = json.load(f)
            assert source['config']['configBean.mongoConfig.collection'] == 'adtech'
        assert result.exit_code == 0

    def test_create(self, cli_runner, name, options, value, timestamp, timestamp_type, properties):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"""test_mongo\n{name}\nclicks\n{value}\n\n{timestamp}\n{timestamp_type}\nver Country\nExchange optional_dim\n{properties}\n""")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"""{value}\n\n\n\n\n\n\n\n""")
        assert result.exit_code == 0

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()
