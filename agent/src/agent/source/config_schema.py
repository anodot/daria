import click
import re

from urllib.parse import urlparse, parse_qs, urljoin


def prompt_mongo_config(default_config, advanced=False):
    config = dict()
    config['configBean.mongoConfig.connectionString'] = click.prompt('Connection string',
                                                                     type=click.STRING,
                                                                     default=default_config.get(
                                                                         'configBean.mongoConfig.connectionString'))
    config['configBean.mongoConfig.username'] = click.prompt('Username',
                                                             type=click.STRING,
                                                             default=default_config.get(
                                                                 'configBean.mongoConfig.username', ''))
    config['configBean.mongoConfig.password'] = click.prompt('Password',
                                                             type=click.STRING,
                                                             default=default_config.get(
                                                                 'configBean.mongoConfig.password', ''))
    config['configBean.mongoConfig.authSource'] = click.prompt('Authentication Source',
                                                               type=click.STRING,
                                                               default=default_config.get(
                                                                   'configBean.mongoConfig.authSource', ''))
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

    if config['configBean.mongoConfig.username'] == '':
        config['configBean.mongoConfig.authenticationType'] = 'NONE'

    return config


def prompt_kafka_config(default_config, advanced=False):
    config = dict()
    config['kafkaConfigBean.metadataBrokerList'] = click.prompt('Kafka broker connection string',
                                                                type=click.STRING,
                                                                default=default_config.get(
                                                                    'kafkaConfigBean.metadataBrokerList'))
    config['kafkaConfigBean.consumerGroup'] = click.prompt('Consumer group',
                                                           type=click.STRING,
                                                           default=default_config.get('kafkaConfigBean.consumerGroup',
                                                                                      'anodotAgent'))
    config['kafkaConfigBean.topic'] = click.prompt('Topic', type=click.STRING,
                                                   default=default_config.get('kafkaConfigBean.topic'))
    config['kafkaConfigBean.kafkaAutoOffsetReset'] = click.prompt('Initial offset',
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

    if advanced:
        config['kafkaConfigBean.maxBatchSize'] = click.prompt('Max Batch Size (records)',
                                                              type=click.INT,
                                                              default=default_config.get('kafkaConfigBean.maxBatchSize',
                                                                                         1000))
        config['kafkaConfigBean.maxWaitTime'] = click.prompt('Batch Wait Time (ms)',
                                                             type=click.INT,
                                                             default=default_config.get('kafkaConfigBean.maxWaitTime',
                                                                                        1000))

        default_kafka_config = default_config.get('kafkaConfigBean.kafkaConsumerConfigs', '')
        if default_kafka_config:
            default_kafka_config = ' '.join([i['key'] + ':' + i['value'] for i in default_kafka_config])
        kafka_config = click.prompt('Kafka Configuration', type=click.STRING, default=default_kafka_config)
        config['kafkaConfigBean.kafkaConsumerConfigs'] = []
        for i in kafka_config.split():
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format')

            config['kafkaConfigBean.kafkaConsumerConfigs'].append({'key': pair[0], 'value': pair[1]})

    return config


def prompt_influx_config(default_config, advanced=False):
    config = dict()
    default_resource_url = default_config.get('conf.resourceUrl', {})
    # default_host = None
    # default_db = None
    # default_limit = 1000
    # if default_resource_url:
    #     url_parsed = urlparse(default_resource_url)
    #     parsed_query = parse_qs(url_parsed.query)
    #     default_db = parsed_query.get('db')
    #     if default_db:
    #         default_db = default_db[0]
    #     q = parsed_query.get('q')
    #     if q:
    #         default_limit_matches = re.search(r'LIMIT\+([0-9]+)\+OFFSET', q[0])
    #         if default_limit_matches:
    #             default_limit = default_limit_matches.group(1)
    #     default_host = url_parsed.netloc
    #     if url_parsed.scheme:
    #         default_host = url_parsed.scheme + '://' + default_host
    influx_host = click.prompt('InfluxDB API url', type=click.STRING, default=default_resource_url.get('host'))
    db = click.prompt('Database', type=click.STRING, default=default_resource_url.get('db'))
    limit = click.prompt('Limit', type=click.INT, default=default_resource_url.get('limit'))
    # query = '/query?db={db}&epoch=s&q=SELECT+{dimensions}+FROM+{metric}+LIMIT+{limit}+OFFSET+${startAt}'.format(**{
    #     'db': db,
    #     'limit': limit,
    #     'dimensions': '{dimensions}',
    #     'metric': '{metric}',
    #     'startAt': '{startAt}',
    # })
    # config['conf.resourceUrl'] = urljoin(influx_host, query)
    config['conf.resourceUrl'] = {
        'host': influx_host,
        'db': db,
        'limit': limit,
    }

    config['conf.pagination.startAt'] = click.prompt('Initial offset ("dd/MM/yy HH:mm")', type=click.STRING, default='')
    config['conf.pagination.rateLimit'] = click.prompt('Wait time, ms', type=click.INT,
                                                       default=default_config.get('conf.pagination.rateLimit', 2000))
    return config


sources_configs = {
    'mongo': prompt_mongo_config,
    'kafka': prompt_kafka_config,
    'influx': prompt_influx_config
}
