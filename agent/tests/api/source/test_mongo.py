from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:
    params = {
        'test_create': [{
            'data': [{
                'name': 'mongo',
                'type': 'mongo',
                'config': {
                    'configBean.mongoConfig.connectionString': 'mongodb://mongo:27017',
                    'configBean.mongoConfig.username': 'root',
                    'configBean.mongoConfig.password': 'root',
                    'configBean.mongoConfig.authSource': 'admin',
                    'configBean.mongoConfig.database': 'test',
                    'configBean.mongoConfig.collection': 'adtech',
                    'configBean.isCapped': False,
                    'configBean.initialOffset': '0',
                    'configBean.mongoConfig.offsetType': 'OBJECTID',
                    'configBean.offsetField': '_id',
                    'configBean.batchSize': 1000,
                    'configBean.maxBatchWaitTime': '10',
                }
            }],
            'er': b'[{"config":{"configBean.batchSize":1000,"configBean.initialOffset":"0","configBean.isCapped":false,"configBean.maxBatchWaitTime":"10","configBean.mongoConfig.authSource":"admin","configBean.mongoConfig.authenticationType":"USER_PASS","configBean.mongoConfig.collection":"adtech","configBean.mongoConfig.connectionString":"mongodb://mongo:27017","configBean.mongoConfig.database":"test","configBean.mongoConfig.offsetType":"OBJECTID","configBean.mongoConfig.password":"root","configBean.mongoConfig.username":"root","configBean.offsetField":"_id"},"name":"mongo","type":"mongo"}]\n'
        }],
        'test_edit': [{
            'data': [{
                'name': 'mongo',
                'config': {
                    'configBean.mongoConfig.connectionString': 'mongodb://mongo:27017',
                    'configBean.mongoConfig.username': 'root',
                    'configBean.mongoConfig.password': 'root',
                    'configBean.mongoConfig.authSource': 'admin',
                    'configBean.mongoConfig.database': 'test',
                    'configBean.mongoConfig.collection': 'adtech',
                    'configBean.isCapped': True,
                    'configBean.initialOffset': '1',
                    'configBean.mongoConfig.offsetType': 'OBJECTID',
                    'configBean.offsetField': '_id',
                    'configBean.batchSize': 1001,
                    'configBean.maxBatchWaitTime': '11',
                }
            }],
            'er': b'[{"config":{"configBean.batchSize":1001,"configBean.initialOffset":"1","configBean.isCapped":true,"configBean.maxBatchWaitTime":"11","configBean.mongoConfig.authSource":"admin","configBean.mongoConfig.authenticationType":"USER_PASS","configBean.mongoConfig.collection":"adtech","configBean.mongoConfig.connectionString":"mongodb://mongo:27017","configBean.mongoConfig.database":"test","configBean.mongoConfig.offsetType":"OBJECTID","configBean.mongoConfig.password":"root","configBean.mongoConfig.username":"root","configBean.offsetField":"_id"},"name":"mongo","type":"mongo"}]\n'
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
        assert result.data == b'["mongo"]\n'

    def test_delete(self, client):
        client.delete('sources/mongo')
        assert client.get('/sources').data == b'[]\n'
