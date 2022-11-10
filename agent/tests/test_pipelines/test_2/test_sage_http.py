import pytest

from datetime import datetime, timezone
from ..test_zpipeline_base import TestPipelineBase, get_schema_id
from ...conftest import get_output, Order


class TestSage(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_dvp'},
        ],
        'test_force_stop': [
            {'name': 'test_sage_value_const', 'check_output_file_name': 'test_sage_value_const_sage.json'},
            {'name': 'test_sage', 'check_output_file_name': 'test_sage_sage.json'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file', 'check_output_file_name': 'test_sage_schema_file_sage.json'},
            {
                'name': 'test_sage_schema_file_dvp',
                'check_output_file_name': f'{get_schema_id("test_sage_schema_file_dvp")}_watermark.json'},
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

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_watermark(self):
        schema_id = get_schema_id('test_sage_schema_file_dvp')
        current_day = datetime.now(timezone.utc)
        day_start_timestamp = current_day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': day_start_timestamp, 'schemaId': schema_id}
