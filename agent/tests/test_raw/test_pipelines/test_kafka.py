from .test_base import TestRawPipelineBase


class TestRawKafka(TestRawPipelineBase):
    __test__ = True
    params = {
        'test_start': [{'name': 'test_kafka_raw'}],
        'test_force_stop': [
            {'name': 'test_kafka_raw', 'check_output_file_name': 'test_kafka_raw.csv'},
        ],
        'test_output': [
            {'file_name': 'test_kafka_raw.csv', 'output_file': 'kafka.csv', 'pipeline_type': 'kafka'},
        ],
        'test_delete_pipeline': [{'name': 'test_kafka_raw'}],
        'test_source_delete': [{'name': 'test_kafka_raw'}],
    }
