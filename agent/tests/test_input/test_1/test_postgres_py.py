import pytest

from datetime import datetime
from ..test_zpipeline_base import TestInputBase


def _get_days_to_backfill():
    return (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1


class TestPostgreSQL(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'postgres_py_sources'}],
        'test_create_with_file': [{'file_name': 'postgres_py_pipelines',
                                   'override_config': {'days_to_backfill': _get_days_to_backfill()}}],
    }
