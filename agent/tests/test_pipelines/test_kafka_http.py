import os
import pytest

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestKafka(TestPipelineBase):
    __test__ = True
    params = {
        'test_source_create': [{'name': 'test_kfk'}, {'name': 'test_running_counters'}],
        'test_create': [
            {'source_name': 'test_kfk', 'name': 'test_kfk_value_const', 'options': ['-a'],
             'value': 'y\nclicksS\ny\n \n ',
             'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
            {'source_name': 'test_kfk', 'name': 'test_kfk_timestamp_ms', 'options': [],
             'value': 'n\nClicks:gauge\nClicks:clicks',
             'timestamp': 'timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'},
            {'source_name': 'test_kfk', 'name': 'test_kfk_timestamp_string', 'options': ['-a'],
             'value': 'y\nclicks\ny\n \n ',
             'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss',
             'advanced_options': 'key1:val1\ntag1:tagval tag2:tagval\n"Country" == "USA"\n/home/kafka_transform.csv'},
            {'source_name': 'test_running_counters', 'name': 'test_kfk_running_counter', 'options': ['-a'],
             'value': 'n\ny\nClicks:running_counter\nClicks:clicks',
             'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n \n \n '},
            {'source_name': 'test_running_counters', 'name': 'test_kfk_running_counter_static_tt', 'options': ['-a'],
             'value': 'n\nn\nClicks:running_counter\ny\nClicks:metric',
             'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n \n \n '},
            {'source_name': 'test_running_counters', 'name': 'test_kfk_running_counter_dynamic_what', 'options': ['-a'],
             'value': 'n\nn\nClicks:agg_type\nClicks:metric',
             'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n \n \n '}
        ],
        'test_create_source_with_file': [{'file_name': 'kafka_sources'}],
        'test_create_with_file': [{'file_name': 'kafka_pipelines'}],
        'test_edit': [{'options': ['test_kfk_value_const'], 'value': 'y\nclicks\n\n'},
                      {'options': ['test_kfk_timestamp_string', '-a'],
                       'value': 'n\nn\nClicks:agg_type\nClicks:metric'}],
        'test_start': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                       {'name': 'test_kfk_timestamp_string'},
                       {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                       {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                       {'name': 'test_kfk_running_counter_dynamic_what'},
                       {'name': 'test_kfk_running_counter_static_tt'}],
        'test_info': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_running_counter'}],
        'test_stop': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                      {'name': 'test_kfk_timestamp_string'},
                      {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                      {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                      {'name': 'test_kfk_running_counter_dynamic_what'},
                       {'name': 'test_kfk_running_counter_static_tt'}],
        'test_output': [
            {'name': 'test_kfk_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_ms', 'output': 'json_value_property.json', 'pipeline_type': 'kafka'},
            {'name': 'test_csv', 'output': 'json_value_property_tags.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_string', 'output': 'json_value_property_transformations.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter', 'output': 'running_counter.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_dynamic_what', 'output': 'running_counter_dynamic_what.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_static_tt', 'output': 'running_counter_static_tt.json',
             'pipeline_type': 'kafka'}

        ],
        'test_delete_pipeline': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                                 {'name': 'test_kfk_timestamp_string'},
                                 {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                                 {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                                 {'name': 'test_kfk_running_counter_dynamic_what'},
                       {'name': 'test_kfk_running_counter_static_tt'}],
        'test_source_delete': [{'name': 'test_kfk'}],
    }

    def test_source_create(self, cli_runner, name):
        result = cli_runner.invoke(source_cli.create,
                                   input=f"kafka\n{name}\nkafka:29092\n{name}\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

    def test_create(self, cli_runner, source_name, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"{source_name}\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n{advanced_options}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
