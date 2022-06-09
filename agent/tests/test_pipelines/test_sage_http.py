import pytest

from datetime import datetime, timezone
from .test_zpipeline_base import TestPipelineBase, get_schema_id
from ..conftest import get_output


class TestSage(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_sage_value_const', 'sleep': 20},
            {'name': 'test_sage', 'sleep': 20},
            {'name': 'test_sage_file', 'sleep': 20},
            {'name': 'test_sage_schema_file', 'sleep': 20},
            {'name': 'test_sage_schema_file_dvp', 'sleep': 20},
        ],
        'test_force_stop': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_dvp'},
        ],
        'test_reset': [
            {'name': 'test_sage_value_const'},
        ],
        'test_output': [
            {'name': 'test_sage_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'sage'},
            {'name': 'test_sage', 'output': 'json_value_property.json', 'pipeline_type': 'sage'},
        ],
        'test_output_schema': [
            {'name': 'test_sage_schema_file', 'output': 'sage_file_schema.json', 'pipeline_type': 'sage'},
        ],
        'test_watermark': [
            {'name': 'test_sage_schema_file_dvp', 'output': 'sage_file_schema.json', 'pipeline_type': 'sage'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_dvp'},
        ],
        'test_source_delete': [
            {'name': 'test_sage'},
            {'name': 'test_sage_1'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_watermark(self):
        schema_id = get_schema_id('test_sage_schema_file_dvp')
        current_day = datetime.now(timezone.utc)
        day_start_timestamp = current_day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': day_start_timestamp, 'schemaId': schema_id}
