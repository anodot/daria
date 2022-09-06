from .test_base import TestRawInputBase


class TestRawKafka(TestRawInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'raw/sources/kafka', 'override_config': {
          "conf.brokerURI": "kafka:29092",
          "conf.topicList": ["test_raw"]
        }}],
        'test_create_raw_with_file': [{'file_name': 'raw/pipelines/kafka'}],
    }
