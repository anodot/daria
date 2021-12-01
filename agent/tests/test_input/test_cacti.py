from datetime import datetime
from .test_zpipeline_base import TestInputBase


def _get_days_to_backfill():
    return (datetime.now() - datetime.fromtimestamp(1619085000).replace(hour=0, minute=0, second=0)).days


class TestCacti(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'cacti_sources'}],
        'test_create_with_file': [{
            'file_name': 'cacti_pipelines',
            'override_config': {'days_to_backfill': _get_days_to_backfill()}
        }],
    }
