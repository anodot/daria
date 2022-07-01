import pytest
import time
from ..test_zpipeline_base import TestPipelineBase, get_schema_id
from ...conftest import get_output


class TestPrtg(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_prtg_xml', 'sleep': 60},
            {'name': 'test_prtg_json', 'sleep': 45},
        ],
        'test_force_stop': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
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

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_output(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_force_stop(self, cli_runner, name):
        super().test_force_stop(cli_runner, name)

    def test_watermark(self, name):
        schema_id = get_schema_id(name)
        watermark_output = get_output(f'{schema_id}_watermark.json')
        assert schema_id == watermark_output.get('schemaId')
        timestamp = watermark_output.get('watermark')
        assert int(time.time()) - timestamp < 300
