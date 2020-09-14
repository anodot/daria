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
                'er': b'"{\\"influx\\": \\"Source influx already exists\\"}"\n',
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
                'status_code': 200,
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
                # todo error codes for tests
                'status_code': 400,
                'er': ""
            }
        ]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        print(result.data)
        assert result.data == er

    def test_edit(self, api_client, data, status_code, er):
        result = api_client.put('/sources', json=list(data))
        assert result.status_code == status_code
        # todo fix after implementing error codes
        if status_code != 400:
            assert result.data == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.data == b'["monitoring","influx"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/influx')
        assert api_client.get('/sources').data ==b'["monitoring"]\n'
