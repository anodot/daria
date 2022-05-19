from .test_zpipeline_base import TestInputBase


class TestTopology(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'topology/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'topology/pipelines'
        }],
    }
