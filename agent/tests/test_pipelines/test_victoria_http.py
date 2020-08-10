import time
import pytest

from ..fixtures import cli_runner
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


class TestVictoria(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'victoria_sources'}],
        'test_create_with_file': [{'file_name': 'victoria_pipelines'}],
        'test_start': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}],
        'test_force_stop': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}],
        'test_output': [
            {'name': 'test_victoria', 'output': 'victoria.jsonl', 'pipeline_type': 'victoria'},
        ],
        'test_delete_pipeline': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}],
        'test_source_delete': [{'name': 'test_victoria'}, {'name': 'test_victoria_2'}],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None):
        pytest.skip()

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_start(self, cli_runner, name):
        super().test_start(cli_runner, name)

    def test_force_stop(self, cli_runner, name):
        time.sleep(10)
        super().test_force_stop(cli_runner, name)
