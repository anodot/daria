import os
import time

import pytest

from agent.modules.constants import LOCAL_DESTINATION_OUTPUT_DIR
from ...test_pipelines.test_zpipeline_base import TestPipelineBase
from ...conftest import Order


class TestRawPipelineBase(TestPipelineBase):
    params = {}

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

    def _check_output_file(self, file_name):
        if file_name:
            self._wait(lambda: get_output(file_name))
            assert get_output(file_name)

    @pytest.mark.order(Order.PIPELINE_START)
    def test_start(self, cli_runner, name: str, sleep: int):
        super(TestRawPipelineBase, self).test_start(cli_runner, name, sleep)

    @pytest.mark.order(Order.PIPELINE_STOP)
    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super(TestRawPipelineBase, self).test_force_stop(cli_runner, name, check_output_file_name)
        # give Streamsets time to send status change to agent
        time.sleep(1)

    @pytest.mark.order(Order.PIPELINE_OUTPUT)
    def test_output(self, file_name, pipeline_type, output_file):
        expected_output = \
            read_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output_file}'))
        actual_output = get_output(file_name)
        assert expected_output == actual_output

    @pytest.mark.order(Order.PIPELINE_DELETE)
    def test_delete_pipeline(self, cli_runner, name):
        super(TestRawPipelineBase, self).test_delete_pipeline(cli_runner, name)

    @pytest.mark.order(Order.SOURCE_DELETE)
    def test_source_delete(self, cli_runner, name):
        super(TestRawPipelineBase, self).test_source_delete(cli_runner, name)


def get_output(file_name) -> list | None:
    if not os.path.isdir(LOCAL_DESTINATION_OUTPUT_DIR):
        return None
    for filename in os.listdir(LOCAL_DESTINATION_OUTPUT_DIR):
        if filename == file_name:
            return read_file(os.path.join(LOCAL_DESTINATION_OUTPUT_DIR, filename))


def read_file(file: str) -> list:
    lines = []
    with open(file) as f:
        for line in f.readlines():
            lines = line
    return lines
