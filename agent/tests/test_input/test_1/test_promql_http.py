from datetime import datetime
from ..test_zpipeline_base import TestInputBase


def _get_days_to_backfill():
    return (datetime.now() - datetime(year=2022, month=2, day=1)).days + 1


class TestPromQL(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'promql/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'promql/pipelines',
            'override_config': {
                'days_to_backfill': _get_days_to_backfill()
            }
        }],
    }
