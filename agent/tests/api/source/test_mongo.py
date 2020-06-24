from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:
    params = {
        'test_create': {
            'name': 'mongo',
            'type': 'mongo',
            'url': 'mongodb://mongo:27017',
            'username': 'root',
            'password': 'root',
            'authentication_source': 'admin',
            'database': 'test',
            'collection': 'adtech',
            'is_capped': False,
            'initial_offset': 0,
            'offset_type': 'OBJECTID',
            'offset_field': '_id',
            'batch_size': 1000,
            'max_batch_wait_seconds': 5,
        }
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
