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
                'er': b'[{"config":{"conf.batchWaitTime":10,"conf.brokerURI":"kafka:29092","conf.dataFormat":"JSON","conf.kafkaAutoOffsetReset":"EARLIEST","conf.kafkaOptions":["key:value"],"conf.maxBatchSize":1000,"conf.numberOfThreads":1,"conf.topicList":["test"],"version":"2.0+"},"name":"kafka_source","type":"kafka"}]\n'
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
                'er': b'[{"config":{"conf.batchWaitTime":5,"conf.brokerURI":"http://kafka:29092","conf.dataFormat":"JSON","conf.kafkaAutoOffsetReset":"EARLIEST","conf.kafkaOptions":["key1:value1"],"conf.maxBatchSize":500,"conf.numberOfThreads":2,"conf.topicList":["test1"],"version":"2.0+"},"name":"kafka_source","type":"kafka"}]\n'
            },
        ]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.data == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.data == b'["kafka_source"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/kafka_source')
        assert api_client.get('/sources').data ==b'[]\n'
