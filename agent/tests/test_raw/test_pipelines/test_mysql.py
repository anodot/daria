from .test_base import TestRawPipelineBase


class TestRawMySQL(TestRawPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'mysql_raw'}],
        'test_force_stop': [{'name': 'mysql_raw'}],
        'test_output': [
            {'file_name': 'mysql_raw.json', 'output_file': 'mysql.json', 'pipeline_type': 'mysql'},
        ],
        'test_delete_pipeline': [{'name': 'mysql_raw'}],
        'test_source_delete': [{'name': 'mysql_raw'}]
    }
