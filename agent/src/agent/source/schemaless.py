import click
import json
import os

from .abstract_source import Source, SourceException
from abc import ABCMeta
from agent.tools import infinite_retry, print_dicts, print_json, map_keys, if_validation_enabled


class SchemalessSource(Source, metaclass=ABCMeta):
    CONFIG_DATA_FORMAT = 'conf.dataFormat'
    CONFIG_CSV_MAPPING = 'csv_mapping'

    DATA_FORMAT_JSON = 'JSON'
    DATA_FORMAT_CSV = 'DELIMITED'
    DATA_FORMAT_AVRO = 'AVRO'
    DATA_FORMAT_LOG = 'LOG'

    CONFIG_CSV_TYPE = 'conf.csvFileFormat'
    CONFIG_CSV_TYPE_DEFAULT = 'CSV'
    CONFIG_CSV_TYPE_CUSTOM = 'CUSTOM'
    csv_types = [CONFIG_CSV_TYPE_DEFAULT, CONFIG_CSV_TYPE_CUSTOM]
    CONFIG_CSV_CUSTOM_DELIMITER = 'conf.dataFormatConfig.csvCustomDelimiter'

    CONFIG_AVRO_SCHEMA_SOURCE = 'conf.dataFormatConfig.avroSchemaSource'
    CONFIG_AVRO_SCHEMA = 'conf.dataFormatConfig.avroSchema'
    CONFIG_AVRO_SCHEMA_FILE = 'schema_file'
    CONFIG_AVRO_SCHEMA_REGISTRY_URLS = 'conf.dataFormatConfig.schemaRegistryUrls'
    CONFIG_AVRO_SCHEMA_LOOKUP_MODE = 'conf.dataFormatConfig.schemaLookupMode'

    CONFIG_KEY_DESERIALIZER = 'conf.keyDeserializer'
    CONFIG_VALUE_DESERIALIZER = 'conf.keyDeserializer'

    AVRO_SCHEMA_SOURCE_SOURCE = 'SOURCE'
    AVRO_SCHEMA_SOURCE_INLINE = 'INLINE'
    AVRO_SCHEMA_SOURCE_REGISTRY = 'REGISTRY'
    avro_sources = [AVRO_SCHEMA_SOURCE_SOURCE, AVRO_SCHEMA_SOURCE_INLINE, AVRO_SCHEMA_SOURCE_REGISTRY]

    AVRO_LOOKUP_SUBJECT = 'SUBJECT'
    AVRO_LOOKUP_ID = 'ID'
    AVRO_LOOKUP_AUTO = 'AUTO'
    avro_lookup_modes = [AVRO_LOOKUP_SUBJECT, AVRO_LOOKUP_ID, AVRO_LOOKUP_AUTO]

    CONFIG_AVRO_LOOKUP_ID = 'conf.dataFormatConfig.schemaId'
    CONFIG_AVRO_LOOKUP_SUBJECT = 'conf.dataFormatConfig.subject'

    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'conf.batchWaitTime'

    CONFIG_GROK_PATTERN_DEFINITION = 'conf.dataFormatConfig.grokPatternDefinition'
    CONFIG_GROK_PATTERN = 'conf.dataFormatConfig.grokPattern'

    data_formats = [DATA_FORMAT_JSON, DATA_FORMAT_CSV, DATA_FORMAT_AVRO, DATA_FORMAT_LOG]

    @infinite_retry
    def prompt_custom_delimiter(self, default_config):
        self.config[self.CONFIG_CSV_CUSTOM_DELIMITER] = click.prompt('Custom delimiter character',
                                                                     type=click.STRING,
                                                                     default=default_config.get(
                                                                         self.CONFIG_CSV_CUSTOM_DELIMITER)).trim()
        if len(self.config[self.CONFIG_CSV_CUSTOM_DELIMITER]) != 1:
            raise SourceException(f'{self.config[self.CONFIG_CSV_CUSTOM_DELIMITER]} is not a character')

    def prompt_csv(self, default_config):
        self.config[self.CONFIG_CSV_TYPE] = click.prompt('Delimited format type',
                                                         type=click.Choice(self.csv_types),
                                                         default=default_config.get(self.CONFIG_CSV_TYPE))
        if self.config[self.CONFIG_CSV_TYPE] == self.CONFIG_CSV_TYPE_CUSTOM:
            self.prompt_custom_delimiter(default_config)
        self.change_field_names(default_config)

    def prompt_avro_registry(self, default_config):
        self.config[self.CONFIG_AVRO_SCHEMA_REGISTRY_URLS] = click.prompt('Registry Urls', type=click.STRING,
                                                                          value_proc=lambda x: x.split(','),
                                                                          default=default_config.get(
                                                                              self.CONFIG_AVRO_SCHEMA_REGISTRY_URLS))
        self.config[self.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] = click.prompt('Lookup mode',
                                                                        type=click.Choice(self.avro_lookup_modes),
                                                                        default=default_config.get(
                                                                            self.CONFIG_AVRO_SCHEMA_LOOKUP_MODE))
        if self.config[self.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] == self.AVRO_LOOKUP_ID:
            self.config[self.CONFIG_AVRO_LOOKUP_ID] = click.prompt('Schema ID',
                                                                   type=click.STRING,
                                                                   default=default_config.get(
                                                                       self.CONFIG_AVRO_LOOKUP_ID))
        elif self.config[self.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] == self.AVRO_LOOKUP_SUBJECT:
            self.config[self.CONFIG_AVRO_LOOKUP_SUBJECT] = click.prompt('Schema ID',
                                                                        type=click.STRING,
                                                                        default=default_config.get(
                                                                            self.CONFIG_AVRO_LOOKUP_SUBJECT))
        else:
            self.config[self.CONFIG_KEY_DESERIALIZER] = 'CONFLUENT'
            self.config[self.CONFIG_VALUE_DESERIALIZER] = 'CONFLUENT'

    def prompt_avro(self, default_config):
        self.config[self.CONFIG_AVRO_SCHEMA_SOURCE] = click.prompt('Schema location',
                                                                   type=click.Choice(self.avro_sources),
                                                                   default=default_config.get(
                                                                       self.CONFIG_AVRO_SCHEMA_SOURCE))
        if self.config[self.CONFIG_AVRO_SCHEMA_SOURCE] == self.AVRO_SCHEMA_SOURCE_INLINE:
            self.config[self.CONFIG_AVRO_SCHEMA_FILE] = click.prompt('Schema file path', type=click.File(),
                                                                     default=default_config.get(
                                                                         self.CONFIG_AVRO_SCHEMA_FILE))
            self.config[self.CONFIG_AVRO_SCHEMA] = json.dumps(json.load(self.config[self.CONFIG_AVRO_SCHEMA_FILE]))
        elif self.config[self.CONFIG_AVRO_SCHEMA_SOURCE] == self.AVRO_SCHEMA_SOURCE_REGISTRY:
            self.prompt_avro_registry(default_config)

    def validate_grok_file(self):
        if self.config.get('grok_definition_file') and not os.path.isfile(self.config['grok_definition_file']):
            raise click.UsageError('File does not exist')

    @infinite_retry
    def prompt_grok_definition_file(self, default_config):
        self.config['grok_definition_file'] = click.prompt('Grok pattern definitions file path',
                                                           type=click.STRING,
                                                           default=default_config.get('grok_definition_file', ''))
        self.validate_grok_file()

    def prompt_log(self, default_config):
        self.prompt_grok_definition_file(default_config)

        self.config[self.CONFIG_GROK_PATTERN] = click.prompt('Grok pattern',
                                                             type=click.STRING,
                                                             default=default_config.get(self.CONFIG_GROK_PATTERN))

    def prompt_data_format(self, default_config):
        self.config[self.CONFIG_DATA_FORMAT] = click.prompt('Data format',
                                                            type=click.Choice(self.data_formats),
                                                            default=default_config.get(self.CONFIG_DATA_FORMAT,
                                                                                       self.DATA_FORMAT_JSON))
        if self.config[self.CONFIG_DATA_FORMAT] == self.DATA_FORMAT_CSV:
            self.prompt_csv(default_config)
        elif self.config[self.CONFIG_DATA_FORMAT] == self.DATA_FORMAT_AVRO:
            self.prompt_avro(default_config)
        elif self.config[self.CONFIG_DATA_FORMAT] == self.DATA_FORMAT_LOG:
            self.prompt_log(default_config)

        return self.config

    def prompt_batch_size(self, default_config):
        self.config[self.CONFIG_BATCH_SIZE] = click.prompt('Max Batch Size (records)', type=click.IntRange(1),
                                                           default=default_config.get(self.CONFIG_BATCH_SIZE, 1000))
        self.config[self.CONFIG_BATCH_WAIT_TIME] = click.prompt('Batch Wait Time (ms)', type=click.IntRange(1),
                                                                default=default_config.get(
                                                                    self.CONFIG_BATCH_WAIT_TIME,
                                                                    1000))

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

    def set_config(self, config):
        super().set_config(config)

        if self.config.get('grok_definition_file'):
            with open(self.config['grok_definition_file'], 'r') as f:
                self.config[self.CONFIG_GROK_PATTERN_DEFINITION] = f.read()

    def validate(self):
        super().validate()
        self.validate_grok_file()
