import os
import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_pipeline_base import TestPipelineBase, pytest_generate_tests


class TestKafka(TestPipelineBase):
    __test__ = True
    params = {
        'test_create': [
            {'name': 'test_kfk_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n \n ',
             'timestamp': 'timestamp_unix\nunix', 'properties': 'key1:val1'},
            {'name': 'test_kfk_timestamp_ms', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
             'timestamp': 'timestamp_unix_ms\nunix_ms', 'properties': ''},
            {'name': 'test_kfk_timestamp_string', 'options': ['-a'], 'value': 'y\nclicks\ny\n \n ',
             'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss', 'properties': 'key1:val1'}],
        'test_create_source_with_file': [{'file_name': 'kafka_sources'}],
        'test_create_with_file': [{'file_name': 'kafka_pipelines'}],
        'test_edit': [{'options': ['test_kfk_value_const'], 'value': 'y\nclicks\n\n'},
                      {'options': ['test_kfk_timestamp_string', '-a'],
                       'value': 'n\nn\nClicks:agg_type\nClicks:AdType'}],
        'test_start': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                       {'name': 'test_kfk_timestamp_string'},
                       {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                       {'name': 'test_csv'}],
        'test_stop': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                      {'name': 'test_kfk_timestamp_string'},
                      {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                      {'name': 'test_csv'}],
        'test_output': [{'name': 'test_kfk_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'kafka'},
                        {'name': 'test_kfk_timestamp_ms', 'output': 'json_value_property.json', 'pipeline_type': 'kafka'},
                        {'name': 'test_csv', 'output': 'json_value_property.json', 'pipeline_type': 'kafka'},
                        {'name': 'test_kfk_timestamp_string', 'output': 'json_value_property_kafka_adv.json', 'pipeline_type': 'kafka'}],
        'test_delete_pipeline': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                                 {'name': 'test_kfk_timestamp_string'},
                                 {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                                 {'name': 'test_csv'}],
        'test_source_delete': [{'name': 'test_kfk'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input=f"kafka\ntest_kfk\nkafka:29092\ntest_kfk\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_kfk.json'))

    def test_create(self, cli_runner, name, options, value, timestamp, properties):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"test_kfk\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim\n{properties}\n\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
