from datetime import datetime
from .test_zpipeline_base import TestInputBase


def _get_days_to_backfill():
    return (datetime.now() - datetime(year=2017, month=12, day=10)).days


class TestMSSQL(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'mssql_sources'
        }],
        'test_create_with_file': [{
            'file_name': 'jdbc_pipelines_mssql', 'override_config': {'days_to_backfill': _get_days_to_backfill()}
        }],
    }
