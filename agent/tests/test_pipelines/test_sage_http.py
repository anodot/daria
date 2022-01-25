import pytest

from datetime import datetime
from .test_zpipeline_base import TestPipelineBase, get_schema_id, get_expected_schema_output
from ..conftest import get_output


class TestSage(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps', 'sleep': 30},
        ],
        'test_force_stop': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps'},
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
            {'name': 'test_sage_schema_file_fill_gaps', 'output': 'sage_file_schema.json', 'pipeline_type': 'sage'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_sage_value_const'},
            {'name': 'test_sage'},
            {'name': 'test_sage_file'},
            {'name': 'test_sage_schema_file'},
            {'name': 'test_sage_schema_file_fill_gaps'},
        ],
        'test_source_delete': [
            {'name': 'test_sage'},
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

    def test_watermark(self, cli_runner, name, output, pipeline_type):
        expected_output = get_expected_schema_output(name, output, pipeline_type)
        real_output = get_output(f'{name}_{pipeline_type}.json')
        watermark_output = get_output(f'{get_schema_id(name)}_watermark.json')
        assert real_output == expected_output
        assert watermark_output['schemaId'] == get_schema_id(name)
        watermark_ts = datetime.fromtimestamp(watermark_output['watermark'])
        data_latest_ts = datetime.fromtimestamp(real_output[-1]['timestamp'])
        assert (watermark_ts - data_latest_ts).days > 500
