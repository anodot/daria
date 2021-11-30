from agent import source, pipeline
from ..test_zpipeline_base import TestInputBase


class TestDatabricks(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'databricks_sources'}],
        'test_create_with_file': [{'file_name': 'jdbc_pipelines_databricks'}],
    }

    @classmethod
    def teardown_class(cls):
        for _pipeline in pipeline.repository.get_by_type(source.TYPE_DATABRICKS):
            pipeline.manager.delete(_pipeline)
        for _source in source.repository.get_by_type(source.TYPE_DATABRICKS):
            source.manager.delete(_source)
