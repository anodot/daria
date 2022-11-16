import json
import pytest

from ...conftest import get_output, Order
from ..test_zpipeline_base import TestPipelineBase, get_schema_id, get_expected_events_output
from agent import source, pipeline


class TestDirectory(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_dir_csv'},
            {'name': 'test_dir_log'},
            {'name': 'test_dir_json'},
            {'name': 'events_directory'},
            {'name': 'test_dir_dynamic_tags'},
        ],
        'test_stop': [
            {'name': 'test_dir_log'},
            {'name': 'test_dir_json'},
            {'name': 'test_dir_csv'},
            {'name': 'events_directory'},
            {'name': 'test_dir_dynamic_tags'},
        ],
        'test_reset': [{'name': 'test_dir_log'}],
        'test_output_schema': [
            {'name': 'test_dir_csv', 'output': 'directory_csv.json', 'pipeline_type': source.TYPE_DIRECTORY},
            {'name': 'test_dir_json', 'output': 'directory_json.json', 'pipeline_type': source.TYPE_DIRECTORY},
            {'name': 'test_dir_log', 'output': 'directory_log.json', 'pipeline_type': source.TYPE_DIRECTORY},
            {'name': 'test_dir_dynamic_tags', 'output': 'directory_tags.json', 'pipeline_type': source.TYPE_DIRECTORY},
        ],
        'test_delete_pipeline': [
            {'name': 'test_dir_log'},
            {'name': 'test_dir_json'},
            {'name': 'test_dir_csv'},
            {'name': 'events_directory'},
            {'name': 'test_dir_dynamic_tags'},
        ],
        'test_source_delete': [
            {'name': 'test_dir_log'},
            {'name': 'test_dir_json'},
            {'name': 'test_dir_csv'},
            {'name': 'events_directory'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_stop(self, cli_runner, name, check_output_file_name):
        super().test_stop(cli_runner, name, check_output_file_name)

    @pytest.mark.order(Order.PIPELINE_RAW_OUTPUT)
    def test_watermark(self):
        schema_id = get_schema_id('test_dir_json')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': 1512889200.0 + 3600, 'schemaId': schema_id}

    def test_force_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_offset(self):
        pipeline_ = pipeline.repository.get_by_id('test_dir_csv')
        assert pipeline_.offset
        assert json.loads(pipeline_.offset.offset) == {
            "version": 2,
            "offsets": {
                "$com.streamsets.pipeline.stage.origin.spooldir.SpoolDirSource.offset.version$": "1",
                "/home/test-datasets/test-directory-collector/12102017_test.csv": "{\"POS\":\"-1\"}"
            }
        }

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_events_output(self):
        assert get_output('events_directory.json') == get_expected_events_output('events_directory.json')
