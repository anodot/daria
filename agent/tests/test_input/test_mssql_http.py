from datetime import datetime
from agent import source, pipeline
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

    @classmethod
    def teardown_class(cls):
        for _pipeline in pipeline.repository.get_by_type(source.TYPE_MSSQL):
            pipeline.manager.delete(_pipeline)
        for _source in source.repository.get_by_type(source.TYPE_MSSQL):
            source.manager.delete(_source)
