import click
import json
from .abstract_source import Source, SourceException
from agent.tools import infinite_retry, print_dicts, print_json, map_keys, if_validation_enabled


class KafkaSource(Source):
    CONFIG_BROKER_LIST = 'conf.brokerURI'
    CONFIG_CONSUMER_GROUP = 'conf.consumerGroup'
    CONFIG_TOPIC_LIST = 'conf.topicList'
    CONFIG_OFFSET_TYPE = 'conf.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'conf.timestampToSearchOffsets'
    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'conf.batchWaitTime'
    CONFIG_CONSUMER_PARAMS = 'conf.kafkaOptions'
    CONFIG_LIBRARY = 'library'
    CONFIG_VERSION = 'version'
    CONFIG_DATA_FORMAT = 'conf.dataFormat'
    CONFIG_CSV_MAPPING = 'csv_mapping'

    DATA_FORMAT_JSON = 'JSON'
    DATA_FORMAT_CSV = 'DELIMITED'
    DATA_FORMAT_AVRO = 'AVRO'

    CONFIG_AVRO_SCHEMA_SOURCE = 'conf.dataFormatConfig.avroSchemaSource'
    CONFIG_AVRO_SCHEMA = 'conf.dataFormatConfig.avroSchema'
    CONFIG_AVRO_SCHEMA_FILE = 'schema_file'

    AVRO_SCHEMA_SOURCE_SOURCE = 'SOURCE'
    AVRO_SCHEMA_SOURCE_INLINE = 'INLINE'

    OFFSET_EARLIEST = 'EARLIEST'
    OFFSET_LATEST = 'LATEST'
    OFFSET_TIMESTAMP = 'TIMESTAMP'

    TEST_PIPELINE_NAME = 'test_kafka_kjeu4334'

    VALIDATION_SCHEMA_FILE_NAME = 'kafka.json'

    DEFAULT_KAFKA_VERSION = '2.0+'

    version_libraries = {'0.10': 'streamsets-datacollector-apache-kafka_0_11-lib',
                         '0.11': 'streamsets-datacollector-apache-kafka_0_11-lib',
                         '2.0+': 'streamsets-datacollector-apache-kafka_2_0-lib'}

    data_formats = [DATA_FORMAT_JSON, DATA_FORMAT_CSV, DATA_FORMAT_AVRO]

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

        # self.config[self.CONFIG_CONSUMER_GROUP] = click.prompt('Consumer group', type=click.STRING,
        #                                                        default=default_config.get(self.CONFIG_CONSUMER_GROUP,
        #                                                                                   'anodotAgent')).strip()
        self.config[self.CONFIG_TOPIC_LIST] = click.prompt('Topic list', type=click.STRING,
                                                           value_proc=lambda x: x.split(','),
                                                           default=default_config.get(self.CONFIG_TOPIC_LIST))
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

        return self.config

    def prompt_data_format(self, default_config):
        self.config[self.CONFIG_DATA_FORMAT] = click.prompt('Data format',
                                                            type=click.Choice(self.data_formats),
                                                            default=default_config.get(self.CONFIG_DATA_FORMAT,
                                                                                       self.DATA_FORMAT_JSON))
        if self.config[self.CONFIG_DATA_FORMAT] == self.DATA_FORMAT_CSV:
            self.change_field_names(default_config)
        elif self.config[self.CONFIG_DATA_FORMAT] == self.DATA_FORMAT_AVRO:
            default_schema_location = default_config.get(self.CONFIG_AVRO_SCHEMA_SOURCE,
                                                         self.AVRO_SCHEMA_SOURCE_SOURCE)
            schema_in_source = click.confirm('Does messages include schema?',
                                             default=default_schema_location == self.AVRO_SCHEMA_SOURCE_SOURCE)
            if not schema_in_source:
                self.config[self.CONFIG_AVRO_SCHEMA_SOURCE] = self.AVRO_SCHEMA_SOURCE_INLINE
                schema_file = click.prompt('Schema file path', type=click.File(),
                                           default=default_config.get(self.CONFIG_AVRO_SCHEMA_FILE))
                self.config[self.CONFIG_AVRO_SCHEMA] = json.dumps(json.load(schema_file))
            else:
                self.config[self.CONFIG_AVRO_SCHEMA_SOURCE] = self.AVRO_SCHEMA_SOURCE_SOURCE

        self.config[self.CONFIG_BATCH_SIZE] = click.prompt('Max Batch Size (records)', type=click.IntRange(1),
                                                           default=default_config.get(self.CONFIG_BATCH_SIZE, 1000))
        self.config[self.CONFIG_BATCH_WAIT_TIME] = click.prompt('Batch Wait Time (ms)', type=click.IntRange(1),
                                                                default=default_config.get(
                                                                    self.CONFIG_BATCH_WAIT_TIME,
                                                                    1000))

        return self.config

    def update_test_source_config(self, stage):
        if self.CONFIG_VERSION in self.config:
            stage['library'] = self.version_libraries[self.config[self.CONFIG_VERSION]]
        super().update_test_source_config(stage)

    def change_field_names(self, default_config):
        previous_val = default_config.get(self.CONFIG_CSV_MAPPING, {})
        records = self.get_sample_records()
        if records:
            print('Records example:')
            print_dicts(records)
            if previous_val:
                print('Previous mapping:')
                print_dicts(map_keys(records, previous_val))
        self.prompt_field_mapping(records, previous_val)

    @infinite_retry
    def prompt_field_mapping(self, records, previous_val):
        new_names = click.prompt('Change fields names (format - key:val,key2:val2,key3:val3)',
                                 type=click.STRING,
                                 default=','.join([f'{idx}:{item}' for idx, item in previous_val.items()])).strip()
        if not new_names:
            self.config[self.CONFIG_CSV_MAPPING] = {}
            print('Saved default mapping')
            return
        data = {}
        for item in new_names.split(','):
            key_val = item.split(':')
            if not key_val or len(key_val) != 2:
                raise click.UsageError('Wrong format. Correct example: `key:val,key2:val2,key3:val3`')
            data[int(key_val[0])] = key_val[1]

        print('Current mapping:')
        print_dicts(map_keys(records, data))
        if not click.confirm('Confirm?'):
            raise ValueError('Try again')

        self.config[self.CONFIG_CSV_MAPPING] = data

    def validate(self):
        super().validate()
        self.validate_connection()

    def set_config(self, config):
        super().set_config(config)
        self.config[self.CONFIG_LIBRARY] = self.version_libraries[self.config.get(self.CONFIG_VERSION,
                                                                                  self.DEFAULT_KAFKA_VERSION)]

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return

        if self.config.get(self.CONFIG_DATA_FORMAT) == self.DATA_FORMAT_CSV:
            self.sample_data = map_keys(records, self.config.get(self.CONFIG_CSV_MAPPING, {}))
            print_dicts(self.sample_data)
        else:
            self.sample_data = records
            print_json(records)
