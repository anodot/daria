import time
import pytest

from .base import PipelineBaseTest, get_expected_schema_output, get_schema_id
from ..conftest import get_output


class TestSNMP(PipelineBaseTest):
    params = {
        'test_start': [
            {'name': 'snmp', 'sleep': 20},
        ],
        'test_force_stop': [{'name': 'snmp'}],
        'test_output_schema': [
            {'name': 'snmp', 'output': 'snmp.json', 'pipeline_type': 'snmp'},
        ],
        'test_delete_pipeline': [{'name': 'snmp'}],
        'test_source_delete': [{'name': 'snmp'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_output_schema(self, name, pipeline_type, output):
        expected_output = get_expected_schema_output(name, output, pipeline_type)
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        # we send current timestamp, it's hard to test, so I check only that data was sent during the last two minutes
        timestamp = actual_output[0].pop('timestamp')
        assert int(time.time()) - timestamp < 120
        assert actual_output == expected_output
        schema_id = get_schema_id(name)
        watermark = get_output(f'{schema_id}_watermark.json')
        assert schema_id == watermark['schemaId']
        assert timestamp == watermark['watermark']
