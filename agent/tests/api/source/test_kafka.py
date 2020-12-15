import requests


class TestSources:
    params = {
        'test_create': [
            {
                'data': [{
                    'type': 'kafka',
                    'name': 'kafka_source',
                    'config': {
                        'version': '2.0+',
                        'conf.brokerURI': 'kafka:29092',
                        'conf.kafkaOptions': ['key:value'],
                        'conf.topicList': ['test'],
                        'conf.numberOfThreads': 1,
                        'conf.kafkaAutoOffsetReset': 'EARLIEST',
                        'conf.dataFormat': 'JSON',
                        'conf.maxBatchSize': 1000,
                        'conf.batchWaitTime': 10,
                    }
                }],
                'er': [{"config": {"conf.batchWaitTime": 10, "conf.brokerURI": "kafka:29092", "conf.dataFormat": "JSON",
                                   "conf.kafkaAutoOffsetReset": "EARLIEST", "conf.kafkaOptions": ["key:value"],
                                   "conf.maxBatchSize": 1000, "conf.numberOfThreads": 1, "conf.topicList": ["test"],
                                   "version": "2.0+"}, "name": "kafka_source", "type": "kafka"}]
            },
        ],
        'test_edit': [
            {
                'data': [{
                    'name': 'kafka_source',
                    'config': {
                        'version': '2.0+',
                        'conf.brokerURI': 'http://kafka:29092',
                        'conf.kafkaOptions': ['key1:value1'],
                        'conf.topicList': ['test1'],
                        'conf.numberOfThreads': 2,
                        'conf.kafkaAutoOffsetReset': 'EARLIEST',
                        'conf.dataFormat': 'JSON',
                        'conf.maxBatchSize': 500,
                        'conf.batchWaitTime': 5,
                    }
                }],
                'er': [{"config": {"conf.batchWaitTime": 5, "conf.brokerURI": "http://kafka:29092",
                                   "conf.dataFormat": "JSON", "conf.kafkaAutoOffsetReset": "EARLIEST",
                                   "conf.kafkaOptions": ["key1:value1"], "conf.maxBatchSize": 500,
                                   "conf.numberOfThreads": 2, "conf.topicList": ["test1"], "version": "2.0+"},
                        "name": "kafka_source", "type": "kafka"}]
            },
        ]
    }

    def test_create(self, data, er):
        result = requests.post('http://localhost/sources', json=list(data))
        result.raise_for_status()
        assert result.json() == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.json == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.json == ["monitoring", "kafka_source"]

    def test_delete(self, api_client):
        api_client.delete('sources/kafka_source')
        assert api_client.get('/sources').json == ["monitoring"]
