streamsets_username = ''
streamsets_password = ''
streamsets_api_base_url = 'http://localhost:18630'

log_file_path = 'agent.log'

pipelines_config = [{
    'source': 'mongo',
    'source_config': {
        'configBean.mongoConfig.connectionString': 'mongodb://mongo:27017',
        'configBean.mongoConfig.username': 'username',
        'configBean.mongoConfig.password': 'password',
        'configBean.mongoConfig.database': 'adtech',
        'configBean.mongoConfig.collection': 'adtech',
        'configBean.isCapped': False,
        'configBean.initialOffset': '2015-01-01 00:00:00',
    },
    'measurement_name': 'impressions',
    'value_field_name': 'Impressions',
    'timestamp_field_name': 'timestamp',  # column type: integer
    'dimensions': ['AdSize', 'AdType', 'Country', 'Exchange', 'ver'],
    'destination_url': ''
}]

try:
    from config_local import *
except ImportError:
    pass
