import pytest

from ..fixtures import get_input_file_path
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestElastic(TestPipelineBase):
    __test__ = True
    params = {
        'test_create': [
            {'name': 'test_es_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n \n ',
             'timestamp': '_source/timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
            {'name': 'test_es_timestamp_ms', 'options': [], 'value': 'n\n_source/Clicks:gauge\n_source/Clicks:clicks',
             'timestamp': '_source/timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'}],
        'test_create_source_with_file': [{'file_name': 'elastic_sources'}],
        'test_create_with_file': [{'file_name': 'elastic_pipelines'}],
        'test_edit': [{'options': ['test_es_value_const'], 'value': 'y\nclicks\n\n'}],
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

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()
