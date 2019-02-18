import click
import re


def prompt_mongo_config(default_config):
    config = dict()
    config['configBean.mongoConfig.connectionString'] = click.prompt('Connection string',
                                                                     type=click.STRING,
                                                                     default=default_config.get(
                                                                         'configBean.mongoConfig.connectionString'))
    config['configBean.mongoConfig.username'] = click.prompt('Username',
                                                             type=click.STRING,
                                                             default=default_config.get(
                                                                 'configBean.mongoConfig.username'))
    config['configBean.mongoConfig.password'] = click.prompt('Password',
                                                             type=click.STRING,
                                                             default=default_config.get(
                                                                 'configBean.mongoConfig.password'))
    config['configBean.mongoConfig.authSource'] = click.prompt('Authentication Source',
                                                               type=click.STRING,
                                                               default=default_config.get(
                                                                   'configBean.mongoConfig.authSource'))
    config['configBean.mongoConfig.database'] = click.prompt('Database',
                                                             type=click.STRING,
                                                             default=default_config.get(
                                                                 'configBean.mongoConfig.database'))
    config['configBean.mongoConfig.collection'] = click.prompt('Collection',
                                                               type=click.STRING,
                                                               default=default_config.get(
                                                                   'configBean.mongoConfig.collection'))
    config['configBean.isCapped'] = click.prompt('Is collection capped',
                                                 type=click.STRING,
                                                 default=default_config.get('configBean.mongoConfig.isCapped',
                                                                            False))
    config['configBean.initialOffset'] = click.prompt('Initial offset', type=click.STRING,
                                                      default=default_config.get('configBean.initialOffset'))

    config['configBean.offsetType'] = click.prompt('Offset type', type=click.Choice(['OBJECTID', 'STRING', 'DATE']),
                                                   default=default_config.get('configBean.offsetType', 'OBJECTID'))

    config['configBean.offsetField'] = click.prompt('Offset field', type=click.STRING,
                                                    default=default_config.get('configBean.offsetField', '_id'))
    config['configBean.batchSize'] = click.prompt('Batch size', type=click.INT,
                                                  default=default_config.get('configBean.batchSize', 1000))

    default_batch_wait_time = default_config.get('configBean.maxBatchWaitTime')
    if default_batch_wait_time:
        default_batch_wait_time = re.findall(r'\d+', default_batch_wait_time)[0]
    else:
        default_batch_wait_time = '5'
    batch_wait_time = click.prompt('Max batch wait time (seconds)', type=click.STRING, default=default_batch_wait_time)
    config['configBean.maxBatchWaitTime'] = '${' + str(batch_wait_time) + ' * SECONDS}'

    return config


def prompt_kafka_config(default_config):
    config = dict()
    config['kafkaConfigBean.metadataBrokerList'] = click.prompt('Kafka broker url',
                                                                type=click.STRING,
                                                                default=default_config.get(
                                                                    'kafkaConfigBean.metadataBrokerList'))
    config['kafkaConfigBean.zookeeperConnect'] = click.prompt('Zookeeper url',
                                                              type=click.STRING,
                                                              default=default_config.get(
                                                                  'kafkaConfigBean.zookeeperConnect'))
    config['kafkaConfigBean.consumerGroup'] = click.prompt('Consumer group',
                                                           type=click.STRING,
                                                           default=default_config.get('kafkaConfigBean.consumerGroup',
                                                                                      'anodotAgent'))
    config['kafkaConfigBean.topic'] = click.prompt('Topic', type=click.STRING,
                                                   default=default_config.get('kafkaConfigBean.topic'))
    config['kafkaConfigBean.kafkaAutoOffsetReset'] = click.prompt('Offset',
                                                                  type=click.Choice(
                                                                      ['EARLIEST', 'LATEST', 'TIMESTAMP']),
                                                                  default=default_config.get(
                                                                      'kafkaConfigBean.kafkaAutoOffsetReset',
                                                                      'EARLIEST'))
    if config['kafkaConfigBean.kafkaAutoOffsetReset'] == 'TIMESTAMP':
        config['kafkaConfigBean.timestampToSearchOffsets'] = click.prompt(
            'Offset timestamp (unix timestamp in milliseconds)',
            type=click.STRING,
            default=default_config.get('kafkaConfigBean.timestampToSearchOffsets'))

    return config


sources_configs = {
    'mongo': prompt_mongo_config,
    'kafka': prompt_kafka_config
}
