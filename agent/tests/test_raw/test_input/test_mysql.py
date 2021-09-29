import pytest

from datetime import datetime
from ...test_input.test_zpipeline_base import TestInputBase

days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days


class TestRawMySQL(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'raw/sources/mysql'}],
        'test_create_raw_with_file': [{
            'file_name': 'raw/pipelines/mysql',
            'override_config': {'days_to_backfill': days_to_backfill}
        }],
    }

    def test_create_with_file(self, cli_runner, file_name=None, override_config=None):
        pytest.skip()
