from ..test_zpipeline_base import TestInputBase


class TestElastic(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'elastic_sources'}],
        'test_create_with_file': [{'file_name': 'elastic_pipelines'}],
    }
