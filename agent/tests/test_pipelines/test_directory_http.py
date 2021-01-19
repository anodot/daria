import json
import pytest

from ..conftest import get_output
from agent import source
from .test_zpipeline_base import TestPipelineBase, get_expected_output, get_schema_id
from agent import pipeline


class TestDirectory(TestPipelineBase):

    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'directory_sources'}],
        'test_create_with_file': [{'file_name': 'directory_pipelines'}],
        'test_start': [{'name': 'test_dir_csv'}, {'name': 'test_dir_log'}, {'name': 'test_dir_json'}],
        'test_stop': [{'name': 'test_dir_log'}, {'name': 'test_dir_json'}, {'name': 'test_dir_csv'}],
        'test_reset': [{'name': 'test_dir_log'}],
        'test_output': [
            {'name': 'test_dir_csv', 'output': 'directory_csv.json', 'pipeline_type': source.TYPE_DIRECTORY},
            {'name': 'test_dir_json', 'output': 'json_value_property_30.json', 'pipeline_type': source.TYPE_DIRECTORY},
            {'name': 'test_dir_log', 'output': 'log_30.json', 'pipeline_type': source.TYPE_DIRECTORY}
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

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_start(self, cli_runner, name):
        super().test_start(cli_runner, name)

    def test_stop(self, cli_runner, name):
        super().test_stop(cli_runner, name)

    def test_watermark(self):
        schema_id = get_schema_id('test_dir_json')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark':   1512892800.0, 'schemaId': schema_id}

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name, pipeline_type, output):
        expected_output = get_expected_output(name, output, pipeline_type)
        for record in expected_output:
            record['schemaId'] = get_schema_id(name)
        assert get_output(f'{name}_{pipeline_type}.json') == expected_output

    def test_offset(self):
        pipeline_ = pipeline.repository.get_by_name('test_dir_csv')
        assert pipeline_.offset
        assert json.loads(pipeline_.offset.offset) == {"version": 2, "offsets": {"$com.streamsets.pipeline.stage.origin.spooldir.SpoolDirSource.offset.version$": "1", "/home/test-directory-collector/12102017_test.csv": "{\"POS\":\"-1\"}"}}
