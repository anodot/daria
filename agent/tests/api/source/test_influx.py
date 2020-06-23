import pytest

from agent.api import main
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client


class TestSources:
    params = {
        'test_create': [
            {
                'source_type': 'bla',
                'name': '',
                'host': '',
                'username': '',
                'password': '',
                'db': '',
                'delete': '',
                'er': b"['Source type is invalid, available types are influx, kafka, mongo, mysql, postgres, elastic, splunk, directory', 'Please, specify the source name']"
            },
            {
                'source_type': 'influx',
                'name': 'influx_source',
                'host': '',
                'username': '',
                'password': '',
                'db': '',
                'delete': '',
                'er': b'{"db":["This field is required."],"host":["This field is required."]}\n'
            },
            {
                'source_type': 'influx',
                'name': 'influx',
                'host': 'http://localhost:8086',
                'username': 'admin',
                'password': 'admin',
                'db': 'test',
                'delete': '',
                'er': b'{"config":{"db":"test","host":"http://localhost:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}\n'
            },
            {
                'source_type': 'influx',
                'name': 'influx',
                'host': 'http://localhost:8086',
                'username': 'admin',
                'password': 'admin',
                'db': 'test',
                'delete': 'influx',
                'er': b"['Source influx already exists']",
            },
        ]
    }

    def test_create(self, client, source_type, name, host, username, password, db, delete, er):
        result = client.post('/sources', json=dict(
            type=source_type,
            name=name,
            host=host,
            username=username,
            password=password,
            db=db
        ))
        if delete:
            client.delete(f'/sources/{delete}')
        assert result.data == er

    def test_get_delete(self, client):
        client.post('/sources', json=dict(
            type='influx',
            name='delete',
            host='http://localhost:8086',
            db='test'
        ))
        result = client.get('/sources')
        client.delete('sources/delete')
        assert result.data == b'["delete"]\n'
