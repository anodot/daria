from .zbase import InputBaseTest


class TestSNMP(InputBaseTest):
    params = {
        'test_create_source_with_file': [{'file_name': 'snmp_sources'}],
        'test_create_with_file': [{'file_name': 'snmp_pipelines'}],
    }
