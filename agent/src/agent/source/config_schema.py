import click
import re

sources_configs = {
    'mongo': [
        {'name': 'configBean.mongoConfig.connectionString', 'prompt_string': 'Connection string', 'type': click.STRING},
        {'name': 'configBean.mongoConfig.username', 'prompt_string': 'Username', 'type': click.STRING},
        {'name': 'configBean.mongoConfig.password', 'prompt_string': 'Password', 'type': click.STRING},
        {'name': 'configBean.mongoConfig.authSource', 'prompt_string': 'Authentication Source', 'type': click.STRING,
         'default': '',
         'comment': """For delegated authentication, specify alternate database name. 
                        Leave blank for normal authentication"""},
        {'name': 'configBean.mongoConfig.database', 'prompt_string': 'Database', 'type': click.STRING},
        {'name': 'configBean.mongoConfig.collection', 'prompt_string': 'Collection', 'type': click.STRING},
        {'name': 'configBean.isCapped', 'prompt_string': 'Is collection capped', 'type': click.BOOL,
         'default': False},
        {'name': 'configBean.initialOffset', 'prompt_string': 'Initial offset', 'type': click.STRING},
        {'name': 'configBean.offsetType', 'prompt_string': 'Offset type',
         'type': click.Choice(['OBJECTID', 'STRING', 'DATE']), 'default': 'OBJECTID'},
        {'name': 'configBean.offsetField', 'prompt_string': 'Offset field', 'type': click.STRING, 'default': '_id'},
        {'name': 'configBean.batchSize', 'prompt_string': 'Batch size', 'type': click.INT, 'default': 1000},
        {'name': 'configBean.maxBatchWaitTime', 'prompt_string': 'Max batch wait time (seconds)', 'type': click.INT,
         'default': '${5 * SECONDS}', 'expression': lambda x: '${' + str(x) + ' * SECONDS}',
         'reverse_expression': lambda x: re.findall(r'\d+', x)[0]},
    ],
    'kafka': [
        {'name': 'kafkaConfigBean.metadataBrokerList', 'prompt_string': 'Kafka broker url', 'type': click.STRING},
        {'name': 'kafkaConfigBean.zookeeperConnect', 'prompt_string': 'Zookeeper url', 'type': click.STRING},
        {'name': 'kafkaConfigBean.consumerGroup', 'prompt_string': 'Consumer group', 'type': click.STRING,
         'default': 'anodotAgent'},
        {'name': 'kafkaConfigBean.topic', 'prompt_string': 'Topic', 'type': click.STRING},
        # {'name': 'kafkaConfigBean.kafkaAutoOffsetReset', 'prompt_string': 'Offset', 'type': click.Choice(['EARLIEST', 'LATEST', 'TIMESTAMP']), 'default': 'EARLIEST'},
        # {'name': 'kafkaConfigBean.timestampToSearchOffsets', 'prompt_string': 'Offset timestamp', 'type': click.INT, 'default': 0},
    ]
}
