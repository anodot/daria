import pytest

from agent import source
from ..test_zpipeline_base import TestPipelineBase


class TestRRD(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'rrd'},
            {'name': 'rrd_archive'},
        ],
        'test_force_stop': [
            {'name': 'rrd', 'check_output_file_name': 'rrd_rrd.json'},
            {'name': 'rrd_archive', 'check_output_file_name': 'rrd_archive_rrd.json'},
        ],
        'test_output': [
            {'name': 'rrd', 'output': 'rrd_dir.json', 'pipeline_type': source.TYPE_RRD},
            {'name': 'rrd_archive', 'output': 'rrd_archive.json', 'pipeline_type': source.TYPE_RRD},
        ],
        'test_delete_pipeline': [
            {'name': 'rrd'},
            {'name': 'rrd_archive'},
        ],
        'test_source_delete': [
            {'name': 'rrd'},
            {'name': 'rrd_archive'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_watermark(self):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)
