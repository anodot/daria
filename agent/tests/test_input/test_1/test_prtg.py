import pytest
from ..test_zpipeline_base import TestInputBase
from ...conftest import Order


class TestPrtg(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'prtg/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'prtg/pipelines'
        }],
    }

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)
