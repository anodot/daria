from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


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
            'er': b'[{"config":{"conf.httpUris":["http://es:9200"],"conf.index":"test","conf.initialOffset":"now-3d/d","conf.isIncrementalMode":false,"conf.offsetField":"timestamp","conf.queryInterval":"seconds"},"name":"elastic","type":"elastic"}]\n'
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
            'er': b'[{"config":{"conf.httpUris":["http://es:9201"],"conf.index":"test1","conf.initialOffset":"now-3d/d","conf.isIncrementalMode":false,"conf.offsetField":"timestamp","conf.queryInterval":"seconds"},"name":"elastic","type":"elastic"}]\n'
        }]
    }

    def test_create(self, client, data, er):
        result = client.post('/sources', json=list(data))
        assert result.data == er

    def test_edit(self, client, data, er):
        result = client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, client):
        result = client.get('/sources')
        assert result.data == b'["elastic"]\n'

    def test_delete(self, client):
        client.delete('sources/elastic')
        assert client.get('/sources').data == b'[]\n'
