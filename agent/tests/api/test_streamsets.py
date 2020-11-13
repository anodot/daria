import json

from agent.modules import constants


class TestDestination:
    URL = 'http://dc2:18630'

    def test_fail_create(self, api_client):
        result = api_client.post(
            '/streamsets',
            json=[{'wrong': self.URL, 'agent_external_url': constants.AGENT_DEFAULT_URL}]
        )
        print(json.loads(result.data))
        assert result.status_code == 400

    def test_fail_create2(self, api_client):
        result = api_client.post(
            '/streamsets', json=[{'url': self.URL, 'agent_external_url': 'abrakadabra'}]
        )
        print(json.loads(result.data))
        assert result.status_code == 400

    def test_wrong_credentials(self, api_client):
        result = api_client.post(
            '/streamsets',
            json=[{'url': self.URL, 'username': 'anton', 'agent_external_url': constants.AGENT_DEFAULT_URL}]
        )
        print(json.loads(result.data))
        assert result.status_code == 400

    def test_create(self, api_client):
        result = api_client.post(
            '/streamsets', json=[{'url': self.URL, 'agent_external_url': constants.AGENT_DEFAULT_URL}]
        )
        print(json.loads(result.data))
        assert result.status_code == 200

    def test_delete(self, api_client):
        result = api_client.delete(
            '/streamsets', json=[{'url': self.URL, 'agent_external_url': constants.AGENT_DEFAULT_URL}]
        )
        print(json.loads(result.data))
        assert result.status_code == 200
        assert self.URL not in api_client.get('/streamsets').json
