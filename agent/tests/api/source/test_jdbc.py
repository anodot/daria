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
                    'connection_string': 'mysql://root@mysql:3306/test',
                    'hikariConfigBean.username': '',
                    'hikariConfigBean.password': '',
                    'conf.pagination.query_interval': 5,
                }
            }],
            'er': b'[{"config":{"conf.pagination.query_interval":5,"connection_string":"mysql://root@mysql:3306/test","hikariConfigBean.connectionString":"jdbc:mysql://root@mysql:3306/test","hikariConfigBean.password":"","hikariConfigBean.username":""},"name":"mysql","type":"mysql"}]\n'
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
        assert result.data == b'["monitoring","mysql"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/mysql')
        assert api_client.get('/sources').data ==b'["monitoring"]\n'
