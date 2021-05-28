import pytest

from .test_zpipeline_base import TestPipelineBase, get_schema_id
from ..conftest import get_output


class TestInflux(TestPipelineBase):
    __test__ = True

    params = {
        'test_start': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                       {'name': 'test_influx_file_full'}, {'name': 'test_influx_adv'}],
        'test_force_stop': [{'name': 'test_basic'}, {'name': 'test_basic_offset'}, {'name': 'test_influx_file_short'},
                            {'name': 'test_influx_file_full'}, {'name': 'test_influx_adv'}],
        'test_reset': [{'name': 'test_basic'}],
        'test_output': [
            {'name': 'test_influx_file_short', 'output': 'influx.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_file_full', 'output': 'influx_file_full.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_adv', 'output': 'influx_adv.json', 'pipeline_type': 'influx'}
        ],
        'test_output_schema': [
            {'name': 'test_basic', 'output': 'influx_schema.json', 'pipeline_type': 'influx'},
            {'name': 'test_basic_offset', 'output': 'influx_offset_schema.json', 'pipeline_type': 'influx'},
        ],
        'test_delete_pipeline': [{'name': 'test_basic'}, {'name': 'test_basic_offset'},
                                 {'name': 'test_influx_file_short'}, {'name': 'test_influx_file_full'},
                                 {'name': 'test_influx_adv'}],
        'test_source_delete': [{'name': 'test_influx'}, {'name': 'test_influx_offset'}, {'name': 'test_influx_1'}],
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
        initial_offset = 1552222380.0
        interval = 1200000
        schema_id = get_schema_id('test_basic')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': initial_offset + interval, 'schemaId': schema_id}
        initial_offset = 1552999980.0
        schema_id = get_schema_id('test_basic_offset')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': initial_offset + interval, 'schemaId': schema_id}
