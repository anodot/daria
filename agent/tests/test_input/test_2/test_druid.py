from agent import source, pipeline
from ..test_zpipeline_base import TestInputBase


class TestDatabricks(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'jdbc/druid_sources'}],
        'test_create_with_file': [{'file_name': 'jdbc/druid_pipelines'}],
    }

    @classmethod
    def teardown_class(cls):
        for _pipeline in pipeline.repository.get_by_type(source.TYPE_DRUID):
            pipeline.manager.delete(_pipeline)
        for _source in source.repository.get_by_type(source.TYPE_DRUID):
            source.manager.delete(_source)
