import json


class TestMonitoring:

    def test_monitoring(self, api_client):
        result = api_client.get('/monitoring', json=[{}])
        print(json.loads(result.data))
        assert result.status_code == 200
