import pytest

from ..test_zpipeline_base import TestInputBase
from ...conftest import Order
from agent import cli


class TestTopology(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'topology/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'topology/pipelines'
        }],
    }

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create_with_file(self, cli_runner, file_name, override_config):
        self._test_create_with_file(cli_runner, file_name, override_config, cli.pipeline.create_topology)
