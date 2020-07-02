from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:
    params = {
        'test_create': [
            {
                'data': [{
                    'type': 'influx',
                    'name': 'influx',
                    'config': {
                        'host': 'http://influx:8086',
                        'username': 'admin',
                        'password': 'admin',
                        'db': 'test',
                    }
                }],
                'er': b'[{"config":{"db":"test","host":"http://influx:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}]\n'
            },
            {
                'data': [{
                    'type': 'influx',
                    'name': 'influx',
                    'config': {
                        'host': 'http://influx:8086',
                        'username': 'admin',
                        'password': 'admin',
                        'db': 'test',
                    }
                }],
                'er': b'"Source config influx already exists"\n',
            },
        ],
        'test_edit': [
            {
                'data': [{
                    'type': 'influx',
                    'name': 'influx',
                    'config': {
                        'host': 'http://influx:8086',
                        'username': 'admin',
                        'password': 'admin',
                        'db': 'test',
                    }
                }],
                'er': b'[{"config":{"db":"test","host":"http://influx:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}]\n'
            },
            {
                'data': [{
                    'type': 'influx',
                    'name': 'not_existing',
                    'config': {
                        'host': 'http://influx:8086',
                        'username': 'new_shepard',
                        'password': 'new_shepard',
                        'db': 'space',
                    }
                }],
                'er': b'"\'not_existing\' is not one of [\'influx\']\\n\\nFailed validating \'enum\' in schema[\'items\'][\'properties\'][\'name\']:\\n    {\'enum\': [\'influx\'], \'maxLength\': 100, \'minLength\': 1, \'type\': \'string\'}\\n\\nOn instance[0][\'name\']:\\n    \'not_existing\'"\n'
            }
        ]
    }

    def test_create(self, client, data, er):
        result = client.post('/sources', json=list(data))
        print(result.data)
        assert result.data == er

    def test_edit(self, client, data, er):
        result = client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, client):
        result = client.get('/sources')
        assert result.data == b'["influx"]\n'

    def test_delete(self, client):
        client.delete('sources/influx')
        assert client.get('/sources').data == b'[]\n'
