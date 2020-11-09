import json


class TestDestination:
    URL = 'http://dc2:18630'

    def test_fail_create(self, api_client):
        result = api_client.post('/streamsets', json=[{'wrong': self.URL}])
        print(json.loads(result.data))
        assert result.status_code == 400

    def test_create(self, api_client):
        result = api_client.post('/streamsets', json=[{'url': self.URL}])
        print(json.loads(result.data))
        assert result.status_code == 200

    def test_delete(self, api_client):
        result = api_client.delete('/streamsets', json=[{'url': self.URL}])
        print(json.loads(result.data))
        assert result.status_code == 200
        assert self.URL not in api_client.get('/streamsets').json
