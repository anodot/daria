import pytest
import time
from agent import source
from ..test_zpipeline_base import TestPipelineBase, get_schema_id, get_expected_schema_output, drop_key_value
from ...conftest import get_output


class TestPrtg(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
        ],
        'test_force_stop': [
            {'name': 'test_prtg_xml', 'check_output_file_name': f'{get_schema_id("test_prtg_xml")}_watermark.json'},
            {'name': 'test_prtg_json', 'check_output_file_name': f'{get_schema_id("test_prtg_json")}_watermark.json'},
        ],
        'test_output_schema': [
            {'name': 'test_prtg_xml', 'output': 'prtg_xml.json', 'pipeline_type': source.TYPE_PRTG},
            {'name': 'test_prtg_json', 'output': 'prtg_json.json', 'pipeline_type': source.TYPE_PRTG},
        ],
        'test_watermark': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
        ],
        'test_source_delete': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
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

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_watermark(self, name):
        schema_id = get_schema_id(name)
        watermark_output = get_output(f'{schema_id}_watermark.json')
        assert schema_id == watermark_output.get('schemaId')
        timestamp = watermark_output.get('watermark')
        assert int(time.time()) - timestamp < 300

    def test_output_schema(self, name, pipeline_type, output):
        expected_output = get_expected_schema_output(name, output, pipeline_type)
        actual_output = get_output(f'{name}_{pipeline_type}.json')
        # because PRTG uses current timestamp, we drop them output check
        expected_output = [drop_key_value(item, 'timestamp') for item in expected_output]
        actual_output = [drop_key_value(item, 'timestamp') for item in actual_output]
        assert actual_output == expected_output
