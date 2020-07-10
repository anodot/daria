import click
from .schemaless import SchemalessSource
from agent.tools import infinite_retry
from agent import source


class KafkaSource(SchemalessSource):
    CONFIG_BROKER_LIST = 'conf.brokerURI'
    CONFIG_CONSUMER_GROUP = 'conf.consumerGroup'
    CONFIG_TOPIC_LIST = 'conf.topicList'
    CONFIG_OFFSET_TYPE = 'conf.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'conf.timestampToSearchOffsets'

    CONFIG_CONSUMER_PARAMS = 'conf.kafkaOptions'
    CONFIG_N_THREADS = 'conf.numberOfThreads'
    CONFIG_LIBRARY = 'library'
    CONFIG_VERSION = 'version'

    OFFSET_EARLIEST = 'EARLIEST'
    OFFSET_LATEST = 'LATEST'
    OFFSET_TIMESTAMP = 'TIMESTAMP'

    DEFAULT_KAFKA_VERSION = '2.0+'

    version_libraries = {'0.10': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '0.11': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '2.0+': 'streamsets-datacollector-apache-kafka_2_0-lib'}

    def prompt(self, default_config, advanced=False):
        if advanced:
            self.source.config[self.CONFIG_VERSION] = \
                click.prompt('Kafka version', type=click.Choice(self.version_libraries.keys()),
                             default=default_config.get(self.CONFIG_VERSION, self.DEFAULT_KAFKA_VERSION))
        self.prompt_connection(default_config, advanced)
        self.source.config[self.CONFIG_TOPIC_LIST] = \
            click.prompt('Topic list', type=click.STRING, value_proc=lambda x: x.split(','),
                         default=default_config.get(self.CONFIG_TOPIC_LIST))
        self.source.config[self.CONFIG_N_THREADS] = \
            click.prompt('Number of threads', type=click.INT, default=default_config.get(self.CONFIG_N_THREADS, 1))
        self.source.config[self.CONFIG_OFFSET_TYPE] = \
            click.prompt('Initial offset',
                         type=click.Choice([self.OFFSET_EARLIEST, self.OFFSET_LATEST, self.OFFSET_TIMESTAMP]),
                         default=default_config.get(self.CONFIG_OFFSET_TYPE, self.OFFSET_EARLIEST))
        if self.source.config[self.CONFIG_OFFSET_TYPE] == self.OFFSET_TIMESTAMP:
            self.source.config[self.CONFIG_OFFSET_TIMESTAMP] = click.prompt(
                'Offset timestamp (unix timestamp in milliseconds)',
                type=click.STRING,
                default=default_config.get(self.CONFIG_OFFSET_TIMESTAMP)).strip()

        if advanced:
            self.prompt_data_format(default_config)
            self.prompt_batch_size(default_config)

        self.source.set_config(self.source.config)
        return self.source

    def validate(self):
        source.validator.validate_json(self.source)
        self.validate_connection()

    @infinite_retry
    def prompt_connection(self, default_config, advanced=False):
        self.source.config[self.CONFIG_BROKER_LIST] = click.prompt('Kafka broker connection string',
                                                                   type=click.STRING,
                                                                   default=default_config.get(self.CONFIG_BROKER_LIST))
        if advanced:
            self.prompt_consumer_params(default_config)
        self.validate_connection()

    @infinite_retry
    def prompt_consumer_params(self, default_config):
        default_kafka_config = default_config.get(self.CONFIG_CONSUMER_PARAMS, '')
        if default_kafka_config:
            default_kafka_config = ','.join([i['key'] + ':' + i['value'] for i in default_kafka_config])
        kafka_config = click.prompt('Kafka Configuration', type=click.STRING, default=default_kafka_config).strip()
        if not kafka_config:
            return
        self.source.config[self.CONFIG_CONSUMER_PARAMS] = []
        for i in kafka_config.split(','):
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format')

            self.source.config[self.CONFIG_CONSUMER_PARAMS].append({'key': pair[0], 'value': pair[1]})

    def set_config(self, config):
        super().set_config(config)
        self.source.config[self.CONFIG_LIBRARY] = \
            self.version_libraries[self.source.config.get(self.CONFIG_VERSION, self.DEFAULT_KAFKA_VERSION)]
