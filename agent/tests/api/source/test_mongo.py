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
            'er': [{"config": {"configBean.batchSize": 1000, "configBean.initialOffset": "0",
                               "configBean.isCapped": False, "configBean.maxBatchWaitTime": "10",
                               "configBean.mongoConfig.authSource": "admin",
                               "configBean.mongoConfig.authenticationType": "USER_PASS",
                               "configBean.mongoConfig.collection": "adtech",
                               "configBean.mongoConfig.connectionString": "mongodb://mongo:27017",
                               "configBean.mongoConfig.database": "test",
                               "configBean.mongoConfig.offsetType": "OBJECTID",
                               "configBean.mongoConfig.password": "root", "configBean.mongoConfig.username": "root",
                               "configBean.offsetField": "_id"}, "name": "mongo", "type": "mongo"}]
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
            'er': [{"config": {"configBean.batchSize": 1001, "configBean.initialOffset": "1",
                               "configBean.isCapped": True, "configBean.maxBatchWaitTime": "11",
                               "configBean.mongoConfig.authSource": "admin",
                               "configBean.mongoConfig.authenticationType": "USER_PASS",
                               "configBean.mongoConfig.collection": "adtech",
                               "configBean.mongoConfig.connectionString": "mongodb://mongo:27017",
                               "configBean.mongoConfig.database": "test",
                               "configBean.mongoConfig.offsetType": "OBJECTID",
                               "configBean.mongoConfig.password": "root", "configBean.mongoConfig.username": "root",
                               "configBean.offsetField": "_id"}, "name": "mongo", "type": "mongo"}]
        }]
    }

    def test_create(self, api_client, data, er):
        result = api_client.post('/sources', json=list(data))
        assert result.json == er

    def test_edit(self, api_client, data, er):
        result = api_client.put('/sources', json=list(data))
        assert result.json == er

    def test_get(self, api_client):
        result = api_client.get('/sources')
        assert result.json == ["mongo"]

    def test_delete(self, api_client):
        api_client.delete('sources/mongo')
        assert api_client.get('/sources').json == []
