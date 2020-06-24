from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestSources:
    params = {
        'test_create_minimal': [
            {
                'name': '',
                'broker_uri': '',
                'topics': '',
                'er':  b"['Please, specify the source name']"
            },
            {
                'name': 'kafka',
                'broker_uri': '',
                'topics': '',
                'er': b'{"broker_uri":["This field is required."],"topics":[["This field is required."]]}\n'
            },
            {
                'name': 'kafka',
                'version': '2.0+',
                'broker_uri': 'kafka:29092',
                'topics': ['test'],
                'er': b'{"config":{"conf.brokerURI":"kafka:29092","conf.topicList":["test"],"library":"streamsets-datacollector-apache-kafka_2_0-lib"},"name":"kafka","type":"kafka"}\n'
            },
        ],
        'test_create_full': [
            {
                'name': 'kafka_source',
                'version': 'asdfasdf',
                'broker_uri': 'kafka:29092',
                'configuration': '',
                'topics': ['test'],
                'num_of_threads': '',
                'initial_offset': 'sdafasf',
                'data_format': 'asdfdas',
                'max_batch_size': '',
                'batch_wait_time': '',
                'override_field_names': '',
                'er': b'{"batch_wait_time":["Not a valid integer value"],"data_format":["asdfdas value is invalid, available values are JSON, DELIMITED, AVRO"],"initial_offset":["sdafasf value is invalid, available values are EARLIEST, LATEST, conf.timestampToSearchOffsets"],"max_batch_size":["Not a valid integer value"],"num_of_threads":["Not a valid integer value"],"version":["asdfasdf value is invalid, available values are 0.10, 0.11, 2.0+"]}\n'
            },
            {
                'name': 'kafka_source',
                'version': '2.0+',
                'broker_uri': 'kafka:29092',
                'configuration': 'key:value',
                'topics': ['test'],
                'num_of_threads': 1,
                'initial_offset': 'EARLIEST',
                'data_format': 'JSON',
                'max_batch_size': 1000,
                'batch_wait_time': 10,
                'override_field_names': '',
                'er': b'{"config":{"conf.batchWaitTime":10,"conf.brokerURI":"kafka:29092","conf.dataFormat":"JSON","conf.kafkaAutoOffsetReset":"EARLIEST","conf.kafkaOptions":[{"key":"key","value":"value"}],"conf.maxBatchSize":1000,"conf.numberOfThreads":1,"conf.topicList":["test"],"library":"streamsets-datacollector-apache-kafka_2_0-lib","version":"2.0+"},"name":"kafka_source","type":"kafka"}\n'
            },
        ],
        'test_edit_minimal': [
            {
                'name': '',
                'num_of_threads': 2,
                'er': b"['Please, specify the source name']"
            },
            # {
            #     'name': 'kafka_source',
            #     'num_of_threads': 2,
            #     'er': b'{"config":{"conf.batchWaitTime":10,"conf.brokerURI":"kafka:29092","conf.dataFormat":"JSON","conf.kafkaAutoOffsetReset":"EARLIEST","conf.kafkaOptions":[{"key":"key","value":"value"}],"conf.maxBatchSize":1000,"conf.numberOfThreads":2,"conf.topicList":["test"],"library":"streamsets-datacollector-apache-kafka_2_0-lib","version":"2.0+"},"name":"kafka_source","type":"kafka"}\n'
            # }
        ]
    }

    def test_create_minimal(self, client, name, broker_uri, topics, er):
        result = client.post('/sources', json=dict(
            type='kafka',
            name=name,
            broker_uri=broker_uri,
            topics=topics,
        ))
        assert result.data == er

    def test_create_full(self, client, name, version, broker_uri, configuration, topics, num_of_threads, initial_offset, data_format, max_batch_size, batch_wait_time, override_field_names, er):
        result = client.post('/sources', json=dict(
            type='kafka',
            name=name,
            version=version,
            broker_uri=broker_uri,
            configuration=configuration,
            topics=topics,
            num_of_threads=num_of_threads,
            initial_offset=initial_offset,
            data_format=data_format,
            max_batch_size=max_batch_size,
            batch_wait_time=batch_wait_time,
            override_field_names=override_field_names,
        ))
        assert result.data == er

    def test_edit_minimal(self, client, name, num_of_threads, er):
        result = client.put('/sources', json=dict(
            type='kafka',
            name=name,
            num_of_threads=num_of_threads,
        ))
        assert result.data == er

    def test_get(self, client):
        result = client.get('/sources')
        assert result.data == b'["kafka_source","kafka"]\n'

    def test_delete(self, client):
        client.delete('sources/kafka_source')
        client.delete('sources/kafka')
        assert client.get('/sources').data == b'[]\n'
