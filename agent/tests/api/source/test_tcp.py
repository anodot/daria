from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestDirectory:
    params = {
        'test_create': [{
            'data': [{
                'name': 'splunk',
                'type': 'splunk',
                'config': {
                    'conf.ports': ["9999"],
                    'conf.dataFormat': 'JSON',
                }
            }],
            'er': b'[{"config":{"conf.dataFormat":"JSON","conf.ports":["9999"]},"name":"splunk","type":"splunk"}]\n'
        }],
        'test_edit': [{
            'data': [{
                'name': 'splunk',
                'type': 'splunk',
                'config': {
                    'conf.ports': ["19999"],
                    'conf.dataFormat': 'JSON',
                }
            }],
            'er': b'[{"config":{"conf.dataFormat":"JSON","conf.ports":["19999"]},"name":"splunk","type":"splunk"}]\n'
        }]
    }

    def test_create(self, client, data, er):
        result = client.post('/sources', json=list(data))
        assert result.data == er

    def test_edit(self, client, data, er):
        result = client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, client):
        result = client.get('/sources')
        assert result.data == b'["splunk"]\n'

    def test_delete(self, client):
        client.delete('sources/splunk')
        assert client.get('/sources').data == b'[]\n'
