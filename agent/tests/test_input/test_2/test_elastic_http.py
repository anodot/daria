from ..test_zpipeline_base import TestInputBase
from datetime import datetime


def _get_days_to_backfill():
    return (datetime.now() - datetime(year=2022, month=10, day=12)).days + 1


class TestElastic(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'elastic_sources'}],
        'test_create_with_file': [{
            'file_name': 'elastic_pipelines',
            'override_config': {
                'days_to_backfill': _get_days_to_backfill()
            }
        }],
    }
