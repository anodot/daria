import json


class TestMonitoring:

    def test_fail_create(self, api_client):
        result = api_client.post(
            '/metrics',
            json=[{}]
        )
        print(json.loads(result.data))
        assert result.status_code == 200
