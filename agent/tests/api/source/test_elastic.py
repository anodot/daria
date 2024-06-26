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
            'er': [{
                "config": {"conf.httpUris": ["http://es:9200"], "conf.index": "test", "conf.initialOffset": "now-3d/d",
                           "conf.isIncrementalMode": True, "conf.offsetField": "timestamp",
                           "conf.queryInterval": "seconds"},
                "name": "elastic",
                "type": "elastic"
            }]
        }],
        'test_edit': [{
            'data': [{
                'name': 'elastic',
                'config': {
                    'conf.httpUris': ['http://es:9200'],
                    'conf.index': 'test1',
                    'conf.offsetField': 'timestamp_unix_ms',
                    'conf.initialOffset': 'now-3d/d',
                    'conf.queryInterval': 'seconds',
                }
            }],
            'er': [{"config": {"conf.httpUris": ["http://es:9200"], "conf.index": "test1",
                               "conf.initialOffset": "now-3d/d", "conf.isIncrementalMode": True,
                               "conf.offsetField": "timestamp_unix_ms", "conf.queryInterval": "seconds"},
                    "name": "elastic",
                    "type": "elastic"}]
        }]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.json == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.json == er

    def test_delete(self, api_client):
        api_client.delete('sources/elastic')
        assert 'elastic' not in api_client.get('/sources').json
