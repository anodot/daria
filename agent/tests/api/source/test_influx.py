from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:
    params = {
        'test_create': [
            {
                'source_type': 'bla',
                'name': '',
                'host': '',
                'username': '',
                'password': '',
                'db': '',
                'er': b"['Source type is invalid, available types are influx, kafka, mongo, mysql, postgres, elastic, splunk, directory', 'Please, specify the source name']"
            },
            {
                'source_type': 'influx',
                'name': 'influx_source',
                'host': '',
                'username': '',
                'password': '',
                'db': '',
                'er': b'{"db":["This field is required."],"host":["This field is required."]}\n'
            },
            {
                'source_type': 'influx',
                'name': 'influx',
                'host': 'http://localhost:8086',
                'username': 'admin',
                'password': 'admin',
                'db': 'test',
                'er': b'{"config":{"db":"test","host":"http://localhost:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}\n'
            },
            {
                'source_type': 'influx',
                'name': 'influx',
                'host': 'http://localhost:8086',
                'username': 'admin',
                'password': 'admin',
                'db': 'test',
                'er': b"['Source influx already exists']",
            },
        ],
        'test_edit': [
            {
                'name': 'influx',
                'host': 'http://externalhost:8086',
                'username': 'new_shepard',
                'password': 'new_shepard',
                'db': 'space',
                'er': b'{"config":{"db":"space","host":"http://externalhost:8086","password":"new_shepard","username":"new_shepard"},"name":"influx","type":"influx"}\n'
            },
            {
                'name': 'not_existing',
                'host': 'http://externalhost:8086',
                'username': 'new_shepard',
                'password': 'new_shepard',
                'db': 'space',
                'er': b"['Source not_existing does not exist']"
            }
        ]
    }

    def test_create(self, client, source_type, name, host, username, password, db, er):
        result = client.post('/sources', json=dict(
            type=source_type,
            name=name,
            host=host,
            username=username,
            password=password,
            db=db
        ))
        assert result.data == er
    
    def test_edit(self, client, name, host, username, password, db, er):
        result = client.put('/sources', json=dict(
            type='influx',
            name=name,
            host=host,
            username=username,
            password=password,
            db=db
        ))
        assert result.data == er

    def test_get(self, client):
        result = client.get('/sources')
        assert result.data == b'["influx"]\n'

    def test_delete(self, client):
        client.delete('sources/influx')
        assert client.get('/sources').data == b'[]\n'
