from ..test_zpipeline_base import TestInputBase


class TestSNMP(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [
            {'file_name': 'snmp/sources'}
        ],
        'test_create_with_file': [
            {'file_name': 'snmp/pipelines'},
            {'file_name': 'snmp/pipelines_filter'}
        ],
    }
