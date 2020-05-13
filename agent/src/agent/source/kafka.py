import click
from .schemaless import SchemalessSource
from agent.tools import infinite_retry


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

    TEST_PIPELINE_FILENAME = 'test_kafka_kjeu4334'

    VALIDATION_SCHEMA_FILE_NAME = 'kafka.json'

    DEFAULT_KAFKA_VERSION = '2.0+'

    version_libraries = {'0.10': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '0.11': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '2.0+': 'streamsets-datacollector-apache-kafka_2_0-lib'}

    @infinite_retry
    def prompt_connection(self, default_config, advanced=False):
        self.config[self.CONFIG_BROKER_LIST] = click.prompt('Kafka broker connection string',
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
        self.config[self.CONFIG_CONSUMER_PARAMS] = []
        for i in kafka_config.split(','):
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format')

            self.config[self.CONFIG_CONSUMER_PARAMS].append({'key': pair[0], 'value': pair[1]})

    def prompt(self, default_config, advanced=False):
        self.config = {}
        if advanced:
            self.config[self.CONFIG_VERSION] = click.prompt('Kafka version',
                                                            type=click.Choice(self.version_libraries.keys()),
                                                            default=default_config.get(self.CONFIG_VERSION,
                                                                                       self.DEFAULT_KAFKA_VERSION))
        self.prompt_connection(default_config, advanced)

        self.config[self.CONFIG_TOPIC_LIST] = click.prompt('Topic list', type=click.STRING,
                                                           value_proc=lambda x: x.split(','),
                                                           default=default_config.get(self.CONFIG_TOPIC_LIST))
        self.config[self.CONFIG_N_THREADS] = click.prompt('Number of threads', type=click.INT,
                                                          default=default_config.get(self.CONFIG_N_THREADS, 1))
        self.config[self.CONFIG_OFFSET_TYPE] = click.prompt('Initial offset',
                                                            type=click.Choice([self.OFFSET_EARLIEST, self.OFFSET_LATEST,
                                                                               self.OFFSET_TIMESTAMP]),
                                                            default=default_config.get(self.CONFIG_OFFSET_TYPE,
                                                                                       self.OFFSET_EARLIEST))
        if self.config[self.CONFIG_OFFSET_TYPE] == self.OFFSET_TIMESTAMP:
            self.config[self.CONFIG_OFFSET_TIMESTAMP] = click.prompt(
                'Offset timestamp (unix timestamp in milliseconds)',
                type=click.STRING,
                default=default_config.get(self.CONFIG_OFFSET_TIMESTAMP)).strip()

        if advanced:
            self.prompt_data_format(default_config)
            self.prompt_batch_size(default_config)

        return self.config

    def update_test_source_config(self, stage):
        if self.CONFIG_VERSION in self.config:
            self.config['library'] = self.version_libraries[self.config[self.CONFIG_VERSION]]

        super().update_test_source_config(stage)

    def validate(self):
        self.validate_json()
        self.validate_connection()

    def set_config(self, config):
        super().set_config(config)
        self.config[self.CONFIG_LIBRARY] = self.version_libraries[self.config.get(self.CONFIG_VERSION,
                                                                                  self.DEFAULT_KAFKA_VERSION)]