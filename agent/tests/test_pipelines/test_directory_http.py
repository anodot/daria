import os
import pytest

from ..fixtures import cli_runner, get_input_file_path
from agent.pipeline import cli as pipeline_cli, load_object as load_pipeline
from agent.source import cli as source_cli, Source, TYPE_DIRECTORY
from agent.streamsets_api_client import api_client
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestDirectory(TestPipelineBase):

    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'directory_sources'}],
        'test_create_with_file': [{'file_name': 'directory_pipelines'}],
        'test_start': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_stop': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_reset': [{'name': 'test_dir_log'}],
        'test_output': [
            {'name': 'test_dir_csv', 'output': 'json_value_property_30.json', 'pipeline_type': TYPE_DIRECTORY},
            {'name': 'test_dir_json', 'output': 'json_value_property_30.json', 'pipeline_type': TYPE_DIRECTORY},
            {'name': 'test_dir_log', 'output': 'log_30.json', 'pipeline_type': TYPE_DIRECTORY}
        ],
        'test_delete_pipeline': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_source_delete': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input="directory\ntest_dir_csv\n/home/test-directory-collector\n*.csv\nDELIMITED\n\ny\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_dir_csv.json'))

    def test_create(self, cli_runner):
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f"test_dir_csv\ntest_dir_csv\n\nn\nClicks:gauge\nClicks:clicks\ntimestamp_unix\nunix\nver Country\nExchange optional_dim\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline('test_dir_csv')

    def test_edit(self, cli_runner):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()

