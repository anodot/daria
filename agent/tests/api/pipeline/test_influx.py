from agent import pipeline


class TestInflux:
    params = {
        'test_source_create': [{
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
            'er': [{"config": {"db": "test", "host": "http://influx:8086", "password": "admin", "username": "admin"},
                    "name": "influx", "type": "influx"}]
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
                "interval": 5
            }],
            'er': [{"dimensions": {"optional": ["wrong"], "required": []}, "interval": 5,
                    "measurement_name": "wrong", "override_source": {}, "pipeline_id": "test_influx",
                    "properties": {"test": "wrong"}, "source": {"name": "influx"}, "target_type": "gauge",
                    "value": {"constant": "1", "type": "property", "values": ["wrong"]}}]
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
                "interval": 5
            }],
            'er': [{"dimensions": {"optional": ["cpu", "host", "zone"], "required": []}, "interval": 5,
                    "measurement_name": "cpu_test", "override_source": {}, "pipeline_id": "test_influx",
                    "properties": {"test": "val"}, "source": {"name": "influx"}, "target_type": "gauge",
                    "value": {"constant": "1", "type": "property", "values": ["usage_active"]}}]
        }],
    }

    def test_source_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.json == er

    def test_create(self, api_client, data, er):
        result = api_client.post('/pipelines', json=list(data))
        assert result.json == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/pipelines', json=list(data))
        assert result.json == er

    def test_start(self, api_client):
        result = api_client.post('/pipelines/test_influx/start')
        assert result.status_code == 200

    def test_info(self, api_client):
        result = api_client.get('/pipelines/test_influx/info')
        assert result.status_code == 200
        assert len(result.data) != 0

    def test_logs(self, api_client):
        result = api_client.get('/pipelines/test_influx/logs')
        assert result.status_code == 200
        assert len(result.data) != 0

    def test_enable_destination_logs(self, api_client):
        result = api_client.post('/pipelines/test_influx/force-stop')
        assert result.status_code == 200
        result = api_client.post('/pipelines/test_influx/enable-destination-logs')
        assert result.status_code == 200

    def test_disable_destination_logs(self, api_client):
        result = api_client.post('/pipelines/test_influx/disable-destination-logs')
        assert result.status_code == 200

    def test_reset(self, api_client):
        result = api_client.post('/pipelines/test_influx/reset')
        assert result.status_code == 200

    def test_pipeline_failed(self, api_client):
        pipeline_name = 'test_influx'
        pipeline_status = 'RUN_ERROR'
        res = api_client.post('/pipeline-status-change', json={
            "pipeline_status": pipeline_status,
            "pipeline_name": pipeline_name,
            "time": "1970-01-01 00:00:00"
        })
        assert res.status_code == 200
        assert pipeline.repository.get_by_name(pipeline_name).status == pipeline_status

    def test_delete(self, api_client):
        api_client.delete('/pipelines/test_influx')
        result = api_client.get('/pipelines')
        assert result.json == [{"override_source": {}, "pipeline_id": "Monitoring", "source": {"name": "monitoring"}}]

    def test_source_delete(self, api_client):
        api_client.delete('/sources/influx')
        result = api_client.get('/sources')
        assert result.json == ["monitoring"]
