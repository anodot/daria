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
            'er': [{"config": {"conf.pagination.query_interval": 10,
                               "connection_string": "mysql://root@mysql:3306/test", "hikariConfigBean.password": "",
                               "hikariConfigBean.username": ""}, "name": "mysql", "type": "mysql"}]
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
            'er': [{"config": {"conf.pagination.query_interval": 5, "connection_string": "mysql://root@mysql:3306/test",
                               "hikariConfigBean.password": "", "hikariConfigBean.username": ""}, "name": "mysql",
                    "type": "mysql"}]
        }]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.json == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.json == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.json == ["mysql"]

    def test_delete(self, api_client):
        api_client.delete('sources/mysql')
        assert api_client.get('/sources').json == []
