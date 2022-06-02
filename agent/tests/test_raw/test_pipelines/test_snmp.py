from .test_base import TestRawPipelineBase


class TestRawSNMP(TestRawPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'snmp_raw', 'sleep': 25}],
        'test_force_stop': [{'name': 'snmp_raw'}],
        'test_output': [
            {'file_name': 'snmp_raw.csv', 'output_file': 'snmp.json', 'pipeline_type': 'mysql'},
        ],
        'test_delete_pipeline': [{'name': 'snmp_raw'}],
        'test_source_delete': [{'name': 'snmp_raw'}]
    }
