import os

from agent import source, pipeline
from agent.modules import constants
from ..test_zpipeline_base import TestInputBase


class TestActian(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'actian_sources'}],
        'test_create_with_file': [{'file_name': 'actian_pipelines'}],
    }

    @classmethod
    def teardown_class(cls):
        for _pipeline in pipeline.repository.get_by_type(source.TYPE_ACTIAN):
            pipeline.manager.delete(_pipeline)
        for _source in source.repository.get_by_type(source.TYPE_ACTIAN):
            source.manager.delete(_source)
