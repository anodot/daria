from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestJdbc:
    params = {
        'test_create': [{
            'data': [{
                'name': 'mysql',
                'type': 'mysql',
                'config': {
                    'connection_string': 'mysql://root@mysql:3306/test',
                    'hikariConfigBean.username': '',
                    'hikariConfigBean.password': '',
                    'conf.pagination.query_interval': 10,
                }
            }],
            'er': b'[{"config":{"conf.pagination.query_interval":10,"connection_string":"mysql://root@mysql:3306/test","hikariConfigBean.connectionString":"jdbc:mysql://root@mysql:3306/test","hikariConfigBean.password":"","hikariConfigBean.username":""},"name":"mysql","type":"mysql"}]\n'
        }],
        'test_edit': [{
            'data': [{
                'name': 'mysql',
                'type': 'mysql',
                'config': {
                    'connection_string': 'mysql://root@mysql:3306/test-2',
                    'hikariConfigBean.username': 'admin',
                    'hikariConfigBean.password': 'admin',
                    'conf.pagination.query_interval': 5,
                }
            }],
            'er': b'[{"config":{"conf.pagination.query_interval":5,"connection_string":"mysql://root@mysql:3306/test-2","hikariConfigBean.connectionString":"jdbc:mysql://root@mysql:3306/test-2","hikariConfigBean.password":"admin","hikariConfigBean.username":"admin"},"name":"mysql","type":"mysql"}]\n'
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
        assert result.data == b'["mysql"]\n'

    def test_delete(self, client):
        client.delete('sources/mysql')
        assert client.get('/sources').data == b'[]\n'
