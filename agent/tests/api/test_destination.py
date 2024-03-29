class TestDestination:
    params = {
        'test_create_fail': [
            {
                'destination_url': 'http://invalid_destination',
                'data_collection_token': 'test',
                'host_id': 'ABCDEF',
                'access_key': 'fad',
                'er': b'Destination url validation failed',
                'status_code': 400,
            },
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'incorrect_token',
                'host_id': 'ABCDEF',
                'access_key': 'fad',
                'er': b'Data collection token is invalid',
                'status_code': 400,
            },
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'correct_token',
                'host_id': 'ABCDEF',
                'access_key': 'incorrect_key',
                'er': b'Access key is invalid',
                'status_code': 400,
            },
        ],
        'test_create': [
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'correct_token',
                'host_id': 'ABCDEF',
                'access_key': 'correct_key',
                'er': {"access_key": "correct_key", "config": {
                    "conf.client.useProxy": False,
                    "token": "correct_token",
                    "url": "http://dummy_destination",
                    "conf.client.tlsConfig.tlsEnabled": False,
                    "conf.client.tlsConfig.keyStoreFilePath": "/data/truststore.jks",
                    "conf.client.tlsConfig.keyStorePassword": "changeit",
                    "conf.client.tlsConfig.trustStoreFilePath": "/data/truststore.jks",
                    "conf.client.tlsConfig.trustStorePassword": "changeit"
                }, "host_id": "ABCDEF", "type": "http"},
                'status_code': 200,
            },
        ],
        'test_create_with_proxy_fail': [
            {
                'proxy_uri': 'http://incorrect_host',
                'er': b'Proxy data is invalid',
                'status_code': 400
            }
            ],
        'test_create_with_proxy': [
            {
                'proxy_uri': 'http://squid:3128',
                'er': {"access_key": "correct_key", "config": {
                    "conf.client.proxy.password": "",
                    "conf.client.proxy.uri": "http://squid:3128",
                    "conf.client.proxy.username": "",
                    "conf.client.useProxy": True,
                    "token": "correct_token",
                    "url": "http://dummy_destination",
                    "conf.client.tlsConfig.tlsEnabled": False,
                    "conf.client.tlsConfig.keyStoreFilePath": "/data/truststore.jks",
                    "conf.client.tlsConfig.keyStorePassword": "changeit",
                    "conf.client.tlsConfig.trustStoreFilePath": "/data/truststore.jks",
                    "conf.client.tlsConfig.trustStorePassword": "changeit"
                }, "host_id": "ABCDEF", "type": "http"},
                'status_code': 200
            }
        ]
    }

    def test_delete(self, api_client):
        result = api_client.delete('/destination')
        assert result.status_code == 200

    def test_create_fail(self, api_client, destination_url, data_collection_token, er, status_code, host_id,
                         access_key):
        result = api_client.post('/destination', json=dict(
            destination_url=destination_url,
            data_collection_token=data_collection_token,
            host_id=host_id,
            access_key=access_key
        ))
        # cleanup
        api_client.delete('/destination')
        assert result.data.startswith(er)
        assert result.status_code == status_code

    def test_create(self, api_client, destination_url, data_collection_token, er, status_code, host_id, access_key):
        result = api_client.post('/destination', json=dict(
            destination_url=destination_url,
            data_collection_token=data_collection_token,
            host_id=host_id,
            access_key=access_key
        ))
        # cleanup
        api_client.delete('/destination')
        assert all(item in er.items() for item in result.json.items())
        assert result.status_code == status_code

    def test_create_with_proxy_fail(self, api_client, proxy_uri, er, status_code):
        result = api_client.post('/destination', json=dict(
            proxy_uri=proxy_uri,
            proxy_username='',
            proxy_password='',
            destination_url='http://dummy_destination',
            data_collection_token='correct_token',
            host_id='ABCDEF',
            access_key='correct_key'
        ))
        print(result.data)
        assert result.data == er
        assert result.status_code == status_code

    def test_create_with_proxy(self, api_client, proxy_uri, er, status_code):
        result = api_client.post('/destination', json=dict(
            proxy_uri=proxy_uri,
            proxy_username='',
            proxy_password='',
            destination_url='http://dummy_destination',
            data_collection_token='correct_token',
            host_id='ABCDEF',
            access_key='correct_key'
        ))
        print(result.data)
        assert all(item in er.items() for item in result.json.items())
        assert result.status_code == status_code
