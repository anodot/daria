from .test_base import TestRawPipelineBase
import pytest


class TestRawMySQL(TestRawPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ],
        'test_force_stop': [
            {'name': 'mysql_raw_json', 'check_output_file_name': 'mysql_raw_json.json'},
            {'name': 'mysql_raw_csv', 'check_output_file_name': 'mysql_raw_csv.csv'}
        ],

        # TODO: fix the test
        # 'test_output': [
        #     {'file_name': 'mysql_raw_json.json', 'output_file': 'mysql.json', 'pipeline_type': 'mysql'},
        #     {'file_name': 'mysql_raw_csv.csv', 'output_file': 'mysql.csv', 'pipeline_type': 'mysql'},
        # ],
        'test_delete_pipeline': [
            {'name': 'mysql_raw_json'},
            {'name': 'mysql_raw_csv'}
        ],
        'test_source_delete': [
            {'name': 'mysql_raw'},
        ]
    }

    def test_output(self, file_name, pipeline_type, output_file):
        pytest.skip()
