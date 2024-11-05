import pytest
from ..test_zpipeline_base import TestInputBase
from ...conftest import Order


class TestDynatrace(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [
            {'file_name': 'dynatrace/sources'},
        ],
    }

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)
