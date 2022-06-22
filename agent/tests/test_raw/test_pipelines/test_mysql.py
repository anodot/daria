from .test_base import TestRawPipelineBase


class TestRawMySQL(TestRawPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ],
        'test_force_stop': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ],
        'test_output': [
            {'file_name': 'mysql_raw_json.json', 'output_file': 'mysql.json', 'pipeline_type': 'mysql'},
            {'file_name': 'mysql_raw_csv.csv', 'output_file': 'mysql.csv', 'pipeline_type': 'mysql'},
        ],
        'test_delete_pipeline': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ],
        'test_source_delete': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ]
    }
