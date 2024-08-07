import click

from .schemaless import SchemalessPrompter
from agent.modules.tools import infinite_retry
from agent import source


class KafkaBuilder(SchemalessPrompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config, advanced)
        self.source.config[source.KafkaSource.CONFIG_TOPIC_LIST] = \
            click.prompt('Topic list', type=click.STRING,
                         default=default_config.get(source.KafkaSource.CONFIG_TOPIC_LIST))
        self.source.config[source.KafkaSource.CONFIG_N_THREADS] = \
            click.prompt('Number of threads', type=click.INT,
                         default=default_config.get(source.KafkaSource.CONFIG_N_THREADS, 1))
        self.source.config[source.KafkaSource.CONFIG_OFFSET_TYPE] = \
            click.prompt('Initial offset',
                         type=click.Choice([source.KafkaSource.OFFSET_EARLIEST, source.KafkaSource.OFFSET_LATEST,
                                            source.KafkaSource.OFFSET_TIMESTAMP]),
                         default=default_config.get(source.KafkaSource.CONFIG_OFFSET_TYPE,
                                                             source.KafkaSource.OFFSET_EARLIEST))
        if self.source.config[source.KafkaSource.CONFIG_OFFSET_TYPE] == source.KafkaSource.OFFSET_TIMESTAMP:
            self.source.config[source.KafkaSource.CONFIG_OFFSET_TIMESTAMP] = click.prompt(
                'Offset timestamp (unix timestamp in milliseconds)',
                type=click.STRING,
                default=default_config.get(source.KafkaSource.CONFIG_OFFSET_TIMESTAMP)).strip()
        if advanced:
            self.prompt_data_format(default_config)
            self.prompt_batch_size(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config, advanced=False):
        self.source.config[source.KafkaSource.CONFIG_BROKER_LIST] = \
            click.prompt('Kafka broker connection string', type=click.STRING,
                         default=default_config.get(source.KafkaSource.CONFIG_BROKER_LIST))
        if advanced:
            self.prompt_consumer_params(default_config)
        self.validator.validate_connection()
        print('Successfully connected to the source')

    @infinite_retry
    def prompt_consumer_params(self, default_config):
        default_kafka_config = default_config.get(source.KafkaSource.CONFIG_CONSUMER_PARAMS, '')
        if default_kafka_config:
            default_kafka_config = ','.join([i['key'] + ':' + i['value'] for i in default_kafka_config])
        kafka_config = click.prompt('Kafka Configuration', type=click.STRING, default=default_kafka_config).strip()
        if not kafka_config:
            return
        self.source.config[source.KafkaSource.CONFIG_CONSUMER_PARAMS] = []
        for i in kafka_config.split(','):
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format')

            self.source.config[source.KafkaSource.CONFIG_CONSUMER_PARAMS].append({'key': pair[0], 'value': pair[1]})
