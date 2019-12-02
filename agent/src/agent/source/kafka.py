import click
import json
import os
import time

from .abstract_source import Source, SourceException
from agent.tools import infinite_retry, print_dicts, if_validation_enabled
from agent.streamsets_api_client import api_client


class KafkaSource(Source):
    CONFIG_BROKER_LIST = 'kafkaConfigBean.metadataBrokerList'
    CONFIG_CONSUMER_GROUP = 'kafkaConfigBean.consumerGroup'
    CONFIG_TOPIC = 'kafkaConfigBean.topic'
    CONFIG_OFFSET_TYPE = 'kafkaConfigBean.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'kafkaConfigBean.timestampToSearchOffsets'
    CONFIG_BATCH_SIZE = 'kafkaConfigBean.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'kafkaConfigBean.maxWaitTime'
    CONFIG_CONSUMER_PARAMS = 'kafkaConfigBean.kafkaConsumerConfigs'
    CONFIG_LIBRARY = 'library'
    CONFIG_VERSION = 'version'
    CONFIG_DATA_FORMAT = 'kafkaConfigBean.dataFormat'
    CONFIG_CSV_MAPPING = 'csv_mapping'

    DATA_FORMAT_JSON = 'JSON'
    DATA_FORMAT_CSV = 'DELIMITED'
    DATA_FORMAT_AVRO = 'AVRO'

    CONFIG_AVRO_SCHEMA_SOURCE = 'kafkaConfigBean.dataFormatConfig.avroSchemaSource'
    CONFIG_AVRO_SCHEMA = 'kafkaConfigBean.dataFormatConfig.avroSchema'
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

    def wait_for_preview(self, preview_id, tries=5, initial_delay=2):
        for i in range(1, tries + 1):
            response = api_client.get_preview_status(self.TEST_PIPELINE_NAME, preview_id)

            if response['status'] not in ['VALIDATING', 'CREATED', 'RUNNING', 'STARTING', 'FINISHING', 'CANCELLING',
                                          'TIMING_OUT']:
                return response

            delay = initial_delay ** i
            if i == tries:
                raise SourceException(f"Can't connect to kafka")
            print(f"Connecting to kafka. Check again after {delay} seconds...")
            time.sleep(delay)

    def create_test_pipeline(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines',
                               self.TEST_PIPELINE_NAME + '.json'), 'r') as f:
            data = json.load(f)

        pipeline_config = data['pipelineConfig']
        new_pipeline = api_client.create_pipeline(self.TEST_PIPELINE_NAME)
        if self.CONFIG_VERSION in self.config:
            pipeline_config['stages'][0]['library'] = self.version_libraries[self.config[self.CONFIG_VERSION]]
        for conf in pipeline_config['stages'][0]['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]
        pipeline_config['uuid'] = new_pipeline['uuid']
        api_client.update_pipeline(self.TEST_PIPELINE_NAME, pipeline_config)

    @if_validation_enabled
    def validate_connection(self):
        self.create_test_pipeline()
        validate_status = api_client.validate(self.TEST_PIPELINE_NAME)
        self.wait_for_preview(validate_status['previewerId'])
        preview_data = api_client.get_preview_data(self.TEST_PIPELINE_NAME, validate_status['previewerId'])
        api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
        if preview_data['status'] == 'INVALID':
            errors = []
            for issue in preview_data['issues']['stageIssues']['KafkaConsumer_01']:
                errors.append(issue['message'])

            raise SourceException('Connection error. ' + '. '.join(errors))

        return True

    @infinite_retry
    def prompt_connection(self, default_config, advanced=False):
        self.config[self.CONFIG_BROKER_LIST] = click.prompt('Kafka broker connection string',
                                                            type=click.STRING,
                                                            default=default_config.get(self.CONFIG_BROKER_LIST))
        if advanced:
            self.prompt_consumer_params(default_config)

        self.validate_connection()
        click.echo('Successfully connected to kafka')

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
            self.config[self.CONFIG_LIBRARY] = self.version_libraries[self.config[self.CONFIG_VERSION]]
        self.prompt_connection(default_config, advanced)

        self.config[self.CONFIG_CONSUMER_GROUP] = click.prompt('Consumer group', type=click.STRING,
                                                               default=default_config.get(self.CONFIG_CONSUMER_GROUP,
                                                                                          'anodotAgent')).strip()
        self.config[self.CONFIG_TOPIC] = click.prompt('Topic', type=click.STRING,
                                                      default=default_config.get(self.CONFIG_TOPIC)).strip()
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

    def sdc_record_map_to_dict(self, record: dict):
        if 'value' in record:
            if type(record['value']) is list:
                return {key: self.sdc_record_map_to_dict(item) for key, item in enumerate(record['value'])}
            elif type(record['value']) is dict:
                return {key: self.sdc_record_map_to_dict(item) for key, item in record['value'].items()}
            else:
                return record['value']
        return record

    def get_sample_records(self, max_records=3):
        self.create_test_pipeline()
        preview = api_client.create_preview(self.TEST_PIPELINE_NAME)
        self.wait_for_preview(preview['previewerId'])
        preview_data = api_client.get_preview_data(self.TEST_PIPELINE_NAME, preview['previewerId'])
        api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
        if not preview_data:
            print('No preview data available')
            return

        try:
            data = preview_data['batchesOutput'][0][0]['output']['KafkaConsumer_01OutputLane15687289061640']
        except ValueError:
            print('No preview data available')
            return
        return [self.sdc_record_map_to_dict(record['value']) for record in data[:max_records]]

    def change_field_names(self, default_config):
        previous_val = default_config.get(self.CONFIG_CSV_MAPPING, {})
        records = self.get_sample_records()
        if records:
            print('Records example:')
            print_dicts(records)
            if previous_val:
                print('Previous mapping:')
                print_dicts(self.map_keys(records, previous_val))
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
        print_dicts(self.map_keys(records, data))
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

    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return

        if self.config.get(self.CONFIG_DATA_FORMAT) == self.DATA_FORMAT_CSV:
            print_dicts(self.map_keys(records, self.config.get(self.CONFIG_CSV_MAPPING, {})))
        else:
            print('\n', '=========')
            for record in records:
                print(json.dumps(record, indent=4, sort_keys=True))
                print('=========')
            print('\n')

    def map_keys(self, records, mapping):
        return [{new_key: record[int(idx)] for idx, new_key in mapping.items()} for record in records]
