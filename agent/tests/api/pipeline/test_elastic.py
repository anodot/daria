from datetime import datetime
from time import sleep


class TestElastic:
    days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
    params = {
        'test_source_create': [{
            'data': [{
                'type': 'elastic',
                'name': 'test_elastic_src',
                'config': {
                    'conf.httpUris': ['es:9200'],
                    'conf.isIncrementalMode': True,
                    'conf.index': 'test',
                    'conf.offsetField': 'timestamp_unix_ms',
                    'conf.initialOffset': f'now-{days_to_backfill}d',
                    'query_interval_sec': 1,
                    'conf.queryInterval': '${1 * SECONDS}'
                }
            }],
            'er': [{
                'config': {
                    'conf.httpUris': ['es:9200'],
                    'conf.index': 'test',
                    'conf.initialOffset': f'now-{days_to_backfill}d',
                    'conf.isIncrementalMode': True,
                    'conf.offsetField': 'timestamp_unix_ms',
                    'conf.queryInterval': '${1 * SECONDS}',
                    'query_interval_sec': 1},
                'name': 'test_elastic_src',
                'type': 'elastic'}]
        }],
        'test_create': [{
            'data': [{
                "source": "test_elastic_src",
                "pipeline_id": "test_elastic_api",
                "measurement_names": {"Clicks":  "clicks"},
                "values": {"Clicks":  "gauge"},
                "dimensions": ["_source/ver", "_source/Country"],
                "uses_schema": False,
                "timestamp": {
                    "type": "unix",
                    "name": "_source/timestamp_unix"
                },
                "query": """{
                    "sort": [{"timestamp_unix_ms": {"order": "asc"}}],
                    "query": {"range": {"timestamp_unix_ms": {"gt": ${OFFSET}}}}
                }"""
            }],
            'er': [{
                'config': {
                    'dimensions': {
                        'optional': ['_source/ver', '_source/Country'],
                        'required': []
                    },
                    'measurement_names': {'Clicks': 'clicks'},
                    'pipeline_id': 'test_elastic_api',
                    'query': '{\n                    "sort": [{"timestamp_unix_ms": {"order": "asc"}}],\n                    "query": {"range": {"timestamp_unix_ms": {"gt": ${OFFSET}}}}\n                }',
                    'timestamp': {'name': '_source/timestamp_unix', 'type': 'unix'},
                    'uses_schema': False,
                    'values': {'Clicks': 'gauge'}
                },
                'id': 'test_elastic_api',
                'override_source': {},
                'schema': {}
            }],
        }],
    }

    def test_source_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.json == er

    def test_create(self, api_client, data, er):
        result = api_client.post('/pipelines', json=list(data))
        assert result.json == er

    def test_start(self, api_client):
        result = api_client.post('/pipelines/test_elastic_api/start')
        assert result.status_code == 200

    def test_info(self, api_client):
        result = api_client.get('/pipelines/test_elastic_api/info')
        sleep(10)
        assert result.status_code == 200
        assert len(result.data) != 0
        assert result.json['metric_errors'] == []

    def test_delete(self, api_client):
        pipeline_id = 'test_elastic_api'
        api_client.delete('/pipelines/test_elastic_api')
        result = api_client.get('/pipelines')
        for obj in result.json:
            if obj['pipeline_id'] == pipeline_id:
                raise Exception

    def test_source_delete(self, api_client):
        source = 'test_elastic_src'
        api_client.delete(f'/sources/{source}')
        result = api_client.get('/sources')
        assert source not in result.json
