import os
import pytest

from ..fixtures import cli_runner, get_input_file_path
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_pipeline_base import TestPipelineBase, pytest_generate_tests


class TestElastic(TestPipelineBase):
    __test__ = True
    params = {
        'test_create': [
            {'name': 'test_es_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n \n ',
             'timestamp': '_source/timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
            {'name': 'test_es_timestamp_ms', 'options': [], 'value': 'n\n_source/Clicks:gauge\n_source/Clicks:clicks',
             'timestamp': '_source/timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'},
            {'name': 'test_es_timestamp_string', 'options': ['-a'], 'value': 'y\nclicks\ny\n \n ',
             'timestamp': '_source/timestamp_string\nstring\nM/d/yyyy H:mm:ss',
             'advanced_options': 'key1:val1\n\n"_source/Country" == "USA"\n/home/elastic_transform.csv'}],
        'test_create_source_with_file': [{'file_name': 'elastic_sources'}],
        'test_create_with_file': [{'file_name': 'elastic_pipelines'}],
        'test_edit': [{'options': ['test_es_value_const'], 'value': 'y\nclicks\n\n'},
                      {'options': ['test_es_timestamp_string', '-a'],
                       'value': 'n\nn\n_source/Clicks:_source/agg_type\n_source/Clicks:_source/AdType'}],
        'test_start': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                       {'name': 'test_es_timestamp_string'},
                       {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_stop': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                      {'name': 'test_es_timestamp_string'},
                      {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_output': [{'name': 'test_es_value_const', 'output': 'json_value_const_adv.json',
                         'pipeline_type': 'elastic'},
                        {'name': 'test_es_timestamp_ms', 'output': 'json_value_property.json',
                         'pipeline_type': 'elastic'},
                        {'name': 'test_es_timestamp_string', 'output': 'json_value_property_transformations.json',
                         'pipeline_type': 'elastic'}],
        'test_delete_pipeline': [{'name': 'test_es_value_const'}, {'name': 'test_es_timestamp_ms'},
                                 {'name': 'test_es_timestamp_string'},
                                 {'name': 'test_es_file_short'}, {'name': 'test_es_file_full'}],
        'test_source_delete': [{'name': 'test_es'}],
    }

    def test_source_create(self, cli_runner):
        query_file_path = get_input_file_path('elastic_query')
        result = cli_runner.invoke(source_cli.create,
                                   input=f"elastic\ntest_es\nhttp://es:9200\ntest\n{query_file_path}\ntimestamp_unix\n0\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_es.json'))

    def test_create(self, cli_runner, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"test_es\n{name}\n\n{value}\n{timestamp}\n_source/ver _source/Country\n_source/Exchange optional_dim ad_type ADTYPE GEN\n{advanced_options}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
