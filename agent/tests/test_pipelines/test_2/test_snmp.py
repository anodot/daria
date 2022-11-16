import time
import pytest

from ..test_zpipeline_base import TestPipelineBase, get_expected_schema_output, get_schema_id
from ...conftest import get_output, Order


class TestSNMP(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'snmp'},
            {'name': 'snmp_multi'},
            {'name': 'snmp_table'},
            {'name': 'snmp_table_filter'},
            {'name': 'snmp_table_indexes'},
        ],
        'test_force_stop': [
            {'name': 'snmp', 'check_output_file_name': f'{get_schema_id("snmp")}_watermark.json'},
            {'name': 'snmp_multi', 'check_output_file_name': f'{get_schema_id("snmp_multi")}_watermark.json'},
            {'name': 'snmp_table', 'check_output_file_name': f'{get_schema_id("snmp_table")}_watermark.json'},
            {'name': 'snmp_table_filter', 'check_output_file_name': f'{get_schema_id("snmp_table_filter")}_watermark.json'},
            {'name': 'snmp_table_indexes', 'check_output_file_name': f'{get_schema_id("snmp_table_indexes")}_watermark.json'},
        ],
        'test_output_schema': [
            {'name': 'snmp', 'output': 'snmp.json', 'pipeline_type': 'snmp'},
            {'name': 'snmp_multi', 'output': 'snmp_multi.json', 'pipeline_type': 'snmp'},
            {'name': 'snmp_table', 'output': 'snmp_table.json', 'pipeline_type': 'snmp'},
            {'name': 'snmp_table_filter', 'output': 'snmp_table_filter.json', 'pipeline_type': 'snmp'},
            {'name': 'snmp_table_indexes', 'output': 'snmp_table_indexes.json', 'pipeline_type': 'snmp'},
        ],
        'test_delete_pipeline': [
            {'name': 'snmp'},
            {'name': 'snmp_multi'},
            {'name': 'snmp_table'},
            {'name': 'snmp_table_filter'},
            {'name': 'snmp_table_indexes'},
        ],
        'test_source_delete': [
            {'name': 'snmp'},
            {'name': 'snmp_multi'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_output_schema(self, name, pipeline_type, output):
        expected_output = get_expected_schema_output(name, output, pipeline_type)

        def check_output():
            actual_output = get_output(f'{name}_{pipeline_type}.json')
            # we send current timestamp, it's hard to test, so I check only that data was sent during the last two minutes
            timestamp = actual_output[0].get('timestamp')
            for output in actual_output:
                output.pop('timestamp')
            return int(time.time()) - timestamp < 120 and actual_output == expected_output

        self._wait(check_output)
        # actual_output = get_output(f'{name}_{pipeline_type}.json')
        # timestamp = actual_output[0].get('timestamp')
        schema_id = get_schema_id(name)
        watermark = get_output(f'{schema_id}_watermark.json')
        assert schema_id == watermark['schemaId']
        # assert timestamp == watermark['watermark']
