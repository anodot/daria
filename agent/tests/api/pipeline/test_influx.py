from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:
    params = {
        'test_source_create': [{
            'data': [{
                'type': 'influx',
                'name': 'influx',
                'config': {
                    'host': 'http://influx:8086',
                    # 'host': 'http://localhost:8086',
                    'username': 'admin',
                    'password': 'admin',
                    'db': 'test',
                }
            }],
            'er': b'[{"config":{"db":"test","host":"http://influx:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}]\n'
            # 'er': b'[{"config":{"db":"test","host":"http://localhost:8086","password":"admin","username":"admin"},"name":"influx","type":"influx"}]\n'
        }],
        'test_create': [{
            'data': [{
                "source": "influx",
                "pipeline_id": "test_influx",
                "measurement_name": "wrong",
                "value": ["wrong"],
                "dimensions": {
                    "required": [],
                    "optional": ["wrong"]
                },
                "target_type": "gauge",
                "properties": {"test": "wrong"},
                "interval": 7000000
            }],
            'er': b'[{"dimensions":{"optional":["wrong"],"required":[]},"interval":7000000,"measurement_name":"wrong","override_source":{},"pipeline_id":"test_influx","properties":{"test":"wrong"},"source":{"name":"influx"},"target_type":"gauge","value":{"constant":"1","type":"property","values":["wrong"]}}]\n'
        }],
        'test_edit': [{
            'data': [{
                "source": "influx",
                "pipeline_id": "test_influx",
                "measurement_name": "cpu_test",
                "value": ["usage_active"],
                "dimensions": {
                    "required": [],
                    "optional": ["cpu", "host", "zone"]
                },
                "target_type": "gauge",
                "properties": {"test": "val"},
                "interval": 7000000
            }],
            'er': b'[{"dimensions":{"optional":["cpu","host","zone"],"required":[]},"interval":7000000,"measurement_name":"cpu_test","override_source":{},"pipeline_id":"test_influx","properties":{"test":"val"},"source":{"name":"influx"},"target_type":"gauge","value":{"constant":"1","type":"property","values":["usage_active"]}}]\n'
        }],
        'test_list': [{
            'er': b'[{"dimensions":{"optional":["cpu","host","zone"],"required":[]},"interval":7000000,"measurement_name":"cpu_test","override_source":{},"pipeline_id":"test_influx","properties":{"test":"val"},"source":{"name":"influx"},"target_type":"gauge","value":{"constant":"1","type":"property","values":["usage_active"]}},{"override_source":{},"pipeline_id":"Monitoring","source":{"name":"monitoring"}}]\n'
        }]
    }

    def test_source_create(self, client, data, er):
        result = client.post('/sources', json=list(data))
        assert result.data == er

    def test_create(self, client, data, er):
        result = client.post('/pipelines', json=list(data))
        assert result.data == er

    def test_edit(self, client, data, er):
        result = client.put('/pipelines', json=list(data))
        assert result.data == er

    def test_start(self, client):
        result = client.post('/pipelines/test_influx/start')
        assert result.status_code == 200

    def test_enable_destination_logs(self, client):
        result = client.post('/pipelines/test_influx/enable-destination-logs')
        assert result.status_code == 200

    def test_disable_destination_logs(self, client):
        result = client.post('/pipelines/test_influx/disable-destination-logs')
        assert result.status_code == 200

    def test_info(self, client):
        result = client.get('/pipelines/test_influx/info')
        assert result.status_code == 200
        assert len(result.data) != 0

    def test_logs(self, client):
        result = client.get('/pipelines/test_influx/logs')
        assert result.status_code == 200
        assert len(result.data) != 0

    def test_stop(self, client):
        result = client.post('/pipelines/test_influx/stop')
        assert result.status_code == 200

    def test_list(self, client, er):
        result = client.get('/pipelines')
        assert result.data == er

    def test_delete(self, client):
        client.delete('/pipelines/test_influx')
        result = client.get('/pipelines')
        assert result.data == b'[{"override_source":{},"pipeline_id":"Monitoring","source":{"name":"monitoring"}}]\n'

    def test_source_delete(self, client):
        client.delete('/sources/influx')
        result = client.get('/sources')
        assert result.data == b'[]\n'
