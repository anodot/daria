from .test_base import TestRawInputBase


class TestRawSNMP(TestRawInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'raw/sources/snmp'}],
        'test_create_raw_with_file': [{'file_name': 'raw/pipelines/snmp'}],
    }
