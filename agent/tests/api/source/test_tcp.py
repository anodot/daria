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

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.data == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.data == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.data == b'["splunk"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/splunk')
        assert api_client.get('/sources').data ==b'[]\n'
