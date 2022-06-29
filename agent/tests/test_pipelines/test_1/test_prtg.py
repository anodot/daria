import pytest
from ..test_zpipeline_base import TestPipelineBase


class TestPrtg(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_prtg_xml'},
            {'name': 'test_prtg_json'},
        ],
        'test_force_stop': [
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
