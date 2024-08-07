from .test_base import TestRawPipelineBase


class TestRawKafka(TestRawPipelineBase):
    __test__ = True
    MAX_TIMES_TO_WAIT = 600
    params = {
        'test_start': [
            {'name': 'kafka_raw_csv'},
            {'name': 'kafka_raw_json'},
        ],
        'test_force_stop': [
            {'name': 'kafka_raw_csv', 'check_output_file_name': 'kafka_raw_csv.csv'},
            {'name': 'kafka_raw_json', 'check_output_file_name': 'kafka_raw_json.json'},
        ],
        'test_output': [
            {'file_name': 'kafka_raw_csv.csv', 'output_file': 'kafka.csv', 'pipeline_type': 'kafka'},
            {'file_name': 'kafka_raw_json.json', 'output_file': 'kafka.json', 'pipeline_type': 'kafka'},
        ],
        'test_delete_pipeline': [
            {'name': 'kafka_raw_csv'},
            {'name': 'kafka_raw_json'},
        ],
        'test_source_delete': [
            {'name': 'test_kafka_raw_csv'},
            {'name': 'test_kafka_raw_json'},
        ],
    }
