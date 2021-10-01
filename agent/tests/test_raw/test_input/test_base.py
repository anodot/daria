import pytest

from agent import cli
from ...test_input.test_zpipeline_base import TestInputBase


class TestRawInputBase(TestInputBase):
    __test__ = False
    params = {}

    def test_create_raw_with_file(self, cli_runner, file_name, override_config: dict):
        self._test_create_with_file(cli_runner, file_name, override_config, cli.pipeline.create_raw)

    def test_create_with_file(self, cli_runner, file_name=None, override_config=None):
        pytest.skip()
