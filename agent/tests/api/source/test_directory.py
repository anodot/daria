class TestDirectory:
    params = {
        'test_create': [{
            'data': [{
                'name': 'directory',
                'type': 'directory',
                'config': {
                    'conf.spoolDir': '/home/test-directory-collector',
                    'conf.filePattern': '*.csv',
                    'conf.dataFormat': 'DELIMITED',
                    'conf.dataFormatConfig.csvFileFormat': 'CUSTOM',
                    'conf.dataFormatConfig.csvCustomDelimiter': '|',
                }
            }],
            'er': b'[{"config":{"conf.dataFormat":"DELIMITED","conf.dataFormatConfig.csvCustomDelimiter":"|","conf.dataFormatConfig.csvFileFormat":"CUSTOM","conf.filePattern":"*.csv","conf.spoolDir":"/home/test-directory-collector"},"name":"directory","type":"directory"}]\n'
        }],
        'test_edit': [{
            'data': [{
                'name': 'directory',
                'type': 'directory',
                'config': {
                    'conf.spoolDir': '/home/test-directory-collector',
                    'conf.filePattern': '*1.csv',
                    'conf.dataFormat': 'DELIMITED',
                    'conf.dataFormatConfig.csvFileFormat': 'CUSTOM',
                    'conf.dataFormatConfig.csvCustomDelimiter': '~',
                }
            }],
            'er': b'[{"config":{"conf.dataFormat":"DELIMITED","conf.dataFormatConfig.csvCustomDelimiter":"~","conf.dataFormatConfig.csvFileFormat":"CUSTOM","conf.filePattern":"*1.csv","conf.spoolDir":"/home/test-directory-collector"},"name":"directory","type":"directory"}]\n'
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
        assert result.data == b'["monitoring","directory"]\n'

    def test_delete(self, api_client):
        api_client.delete('sources/directory')
        assert api_client.get('/sources').data == b'["monitoring"]\n'
