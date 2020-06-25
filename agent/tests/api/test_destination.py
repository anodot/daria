import pytest

from agent.api import main
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client


class TestDestination:
    params = {
        'test_create': [
            {
                'destination_url': 'http://invalid_destination',
                'data_collection_token': 'test',
                'host_id': 'host_id',
                'access_key': '',
                'er': b'Destination URL is invalid',
                'status_code': 400,
            },
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'incorrect_token',
                'host_id': 'host_id',
                'access_key': '',
                'er': b'Data collection token is invalid',
                'status_code': 400,
            },
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'correct_token',
                'host_id': 'host_id',
                'access_key': 'incorrect_key',
                'er': b'Access key is invalid',
                'status_code': 400,
            },
            {
                'destination_url': 'http://dummy_destination',
                'data_collection_token': 'correct_token',
                'host_id': 'host_id',
                'access_key': 'correct_key',
                'er': b'{"access_key":"correct_key","config":{"conf.client.useProxy":false,"conf.resourceUrl":"http://dummy_destination/api/v1/metrics?token=correct_token&protocol=anodot20","monitoring_url":"http://dummy_destination/api/v1/agents?token=correct_token","token":"correct_token","url":"http://dummy_destination"},"host_id":"host_id","type":"http"}\n',
                'status_code': 200,
            },
        ],
        'test_create_with_proxy': [
            {
                'proxy_uri': 'http://incorrect_host',
                'er': b'Proxy data is invalid',
                'status_code': 400
            },
            {
                'proxy_uri': 'http://squid:3128',
                'er': b'{"access_key":"correct_key","config":{"conf.client.proxy.password":"","conf.client.proxy.uri":"http://squid:3128","conf.client.proxy.username":"","conf.client.useProxy":true,"conf.resourceUrl":"http://dummy_destination/api/v1/metrics?token=correct_token&protocol=anodot20","monitoring_url":"http://dummy_destination/api/v1/agents?token=correct_token","token":"correct_token","url":"http://dummy_destination"},"host_id":"host_id","type":"http"}\n',
                'status_code': 200
            }
        ]
    }

    def test_create(self, client, destination_url, data_collection_token, er, status_code, host_id, access_key):
        result = client.post('/destination', json=dict(
            destination_url=destination_url,
            data_collection_token=data_collection_token,
            host_id=host_id,
            access_key=access_key
        ))
        # cleanup
        client.delete('/destination')
        print(result.data)
        assert result.data == er
        assert result.status_code == status_code

    def test_create_with_proxy(self, client, proxy_uri, er, status_code):
        result = client.post('/destination', json=dict(
            proxy_uri=proxy_uri,
            proxy_username='',
            proxy_password='',
            destination_url='http://dummy_destination',
            data_collection_token='correct_token',
            host_id='host_id',
            access_key='correct_key'
        ))
        print(result.data)
        assert result.data == er
        assert result.status_code == status_code
