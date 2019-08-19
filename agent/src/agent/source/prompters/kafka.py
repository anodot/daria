import click

from .prompt_interface import PromptInterface


class PromptKafka(PromptInterface):

    def prompt(self, default_config, advanced=False):
        config = dict()
        config['kafkaConfigBean.metadataBrokerList'] = click.prompt('Kafka broker connection string',
                                                                    type=click.STRING,
                                                                    default=default_config.get(
                                                                        'kafkaConfigBean.metadataBrokerList'))
        config['kafkaConfigBean.consumerGroup'] = click.prompt('Consumer group',
                                                               type=click.STRING,
                                                               default=default_config.get(
                                                                   'kafkaConfigBean.consumerGroup',
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
                                                                  default=default_config.get(
                                                                      'kafkaConfigBean.maxBatchSize',
                                                                      1000))
            config['kafkaConfigBean.maxWaitTime'] = click.prompt('Batch Wait Time (ms)',
                                                                 type=click.INT,
                                                                 default=default_config.get(
                                                                     'kafkaConfigBean.maxWaitTime',
                                                                     1000))

            default_kafka_config = default_config.get('kafkaConfigBean.kafkaConsumerConfigs', '')
            if default_kafka_config:
                default_kafka_config = ' '.join([i['key'] + ':' + i['value'] for i in default_kafka_config])
            kafka_config = click.prompt('Kafka Configuration', type=click.STRING, default=default_kafka_config)
            config['kafkaConfigBean.kafkaConsumerConfigs'] = []
            for i in kafka_config.split(','):
                pair = i.split(':')
                if len(pair) != 2:
                    raise click.UsageError('Wrong format')

                config['kafkaConfigBean.kafkaConsumerConfigs'].append({'key': pair[0], 'value': pair[1]})
        return config
