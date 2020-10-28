class TestElastic:
    params = {
        'test_create': [{
            'data': [{
                'name': 'elastic',
                'type': 'elastic',
                'config': {
                    'conf.httpUris': ['http://es:9200'],
                    'conf.index': 'test',
                    'conf.offsetField': 'timestamp',
                    'conf.initialOffset': 'now-3d/d',
                    'conf.queryInterval': 'seconds',
                }
            }],
            'er': b'[{"config":{"conf.httpUris":["http://es:9200"],"conf.index":"test","conf.initialOffset":"now-3d/d","conf.isIncrementalMode":false,"conf.offsetField":"timestamp","conf.query":null,"conf.queryInterval":"seconds"},"name":"elastic","type":"elastic"}]\n'
        }],
        'test_edit': [{
            'data': [{
                'name': 'elastic',
                'config': {
                    'conf.httpUris': ['http://es:9201'],
                    'conf.index': 'test1',
                    'conf.offsetField': 'timestamp',
                    'conf.initialOffset': 'now-3d/d',
                    'conf.queryInterval': 'seconds',
                }
            }],
            'er': b'[{"config":{"conf.httpUris":["http://es:9201"],"conf.index":"test1","conf.initialOffset":"now-3d/d","conf.isIncrementalMode":false,"conf.offsetField":"timestamp","conf.query":null,"conf.queryInterval":"seconds"},"name":"elastic","type":"elastic"}]\n'
        }]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.data == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.data == b'["monitoring","elastic"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/elastic')
        assert api_client.get('/sources').data ==b'["monitoring"]\n'
