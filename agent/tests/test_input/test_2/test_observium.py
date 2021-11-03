from ..test_zpipeline_base import TestInputBase


class TestObservium(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'observium_sources'}],
        'test_create_with_file': [{'file_name': 'observium_pipelines'}],
    }
