import pytest

from ..fixtures import cli_runner, get_output
from agent.source import TYPE_DIRECTORY
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestDirectory(TestPipelineBase):

    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'directory_sources'}],
        'test_create_with_file': [{'file_name': 'directory_pipelines'}],
        'test_start': [{'name': 'test_dir_csv'}, {'name': 'test_dir_log'}, {'name': 'test_dir_json'}],
        'test_stop': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_reset': [{'name': 'test_dir_log'}],
        'test_output': [
            {'name': 'test_dir_csv', 'output': 'directory_csv.json', 'pipeline_type': TYPE_DIRECTORY},
            {'name': 'test_dir_json', 'output': 'json_value_property_30.json', 'pipeline_type': TYPE_DIRECTORY},
            {'name': 'test_dir_log', 'output': 'log_30.json', 'pipeline_type': TYPE_DIRECTORY}
        ],
        'test_delete_pipeline': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_source_delete': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
    }

    def test_edit(self, cli_runner):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_output_exists(self, cli_runner, name=None):
        pytest.skip()

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_start(self, cli_runner, name):
        super().test_start(cli_runner, name)

    def test_stop(self, cli_runner, name):
        super().test_stop(cli_runner, name)

    def test_watermark(self):
        schema_id = '111111-22222-3333-4444'
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': '1512892800.0', 'schemaId': schema_id}
