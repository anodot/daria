import os
import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, source
from agent.streamsets_api_client import api_client
from .test_pipeline_base import TestPipelineBase, pytest_generate_tests


class TestKafka(TestPipelineBase):
    __test__ = True

    params = {
        'test_source_create': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                               {'name': 'test_kfk_timestamp_kafka'}, {'name': 'test_kfk_timestamp_string'}],
        'test_create': [
            {'name': 'test_kfk_timestamp_kafka', 'options': [], 'value': 'clicks\nClicks\n', 'timestamp': 'y',
             'properties': '', 'source_name': 'test_kfk_timestamp_kafka'},
            {'name': 'test_kfk_value_const', 'options': ['-a'], 'value': 'y\nclicks\n2\nconstant\n',
             'timestamp': 'n\ntimestamp_unix\nunix', 'properties': 'key1:val1',
             'source_name': 'test_kfk_value_const'},
            {'name': 'test_kfk_timestamp_ms', 'options': [], 'value': 'clicks\nClicks\nproperty\n',
             'timestamp': 'n\ntimestamp_unix_ms\nunix_ms', 'properties': '',
             'source_name': 'test_kfk_timestamp_ms'},
            {'name': 'test_kfk_timestamp_string', 'options': ['-a'], 'value': 'y\nclicks\nClicks\nconstant\n',
             'timestamp': 'n\ntimestamp_string\nstring\nM/d/yyyy H:mm:ss', 'properties': 'key1:val1',
             'source_name': 'test_kfk_timestamp_string'}],
        'test_create_with_file': [{'file_name': 'kafka_pipelines'}],
        'test_edit': [{'options': ['test_kfk_value_const'], 'value': '\n1\n\n'},
                      {'options': ['test_kfk_timestamp_string', '-a'],
                       'value': 'n\nAdType\nClicks\nproperty\nagg_type'}],
        'test_start': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                       {'name': 'test_kfk_timestamp_string'}, {'name': 'test_kfk_timestamp_kafka'},
                       {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'}],
        'test_stop': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                      {'name': 'test_kfk_timestamp_string'}, {'name': 'test_kfk_timestamp_kafka'},
                      {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'}],
        'test_output': [{'name': 'test_kfk_value_const', 'output': 'json_value_const_adv.json'},
                        {'name': 'test_kfk_timestamp_ms', 'output': 'json_value_property.json'},
                        {'name': 'test_kfk_timestamp_string', 'output': 'json_value_property_kafka_adv.json'}],
        'test_delete_pipeline': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                                 {'name': 'test_kfk_timestamp_string'}, {'name': 'test_kfk_timestamp_kafka'},
                                 {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'}],
        'test_source_delete': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                               {'name': 'test_kfk_timestamp_kafka'}, {'name': 'test_kfk_timestamp_string'}],
    }

    def test_source_create(self, cli_runner, name):
        result = cli_runner.invoke(source_cli.create,
                                   input=f"kafka\n{name}\nkafka:29092\nstreamsetsDC\n{name}\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source.DIR, f'{name}.json'))

    def test_create(self, cli_runner, source_name, name, options, value, timestamp, properties):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"{source_name}\n{name}\n{value}\n{timestamp}\nver Country\nExchange optional_dim\n{properties}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"{value}\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
