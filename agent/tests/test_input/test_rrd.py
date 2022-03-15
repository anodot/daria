from datetime import datetime
from .test_zpipeline_base import TestInputBase


def _get_days_to_backfill():
    return (datetime.now() - datetime.fromtimestamp(1619085000).replace(hour=0, minute=0, second=0)).days


class TestRRD(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'rrd/sources'}],
        'test_create_with_file': [{
            'file_name': 'rrd/pipelines',
            'override_config': {'days_to_backfill': _get_days_to_backfill()}
        }],
    }
