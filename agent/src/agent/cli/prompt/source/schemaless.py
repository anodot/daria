import click
import json

from .base import Prompter
from abc import ABCMeta
from agent.modules.tools import infinite_retry, print_dicts, print_json, map_keys
from agent import source, pipeline


class SchemalessPrompter(Prompter, metaclass=ABCMeta):
    @infinite_retry
    def prompt_custom_delimiter(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_CSV_CUSTOM_DELIMITER] = \
            click.prompt('Custom delimiter character', type=click.STRING,
                         default=default_config.get(source.SchemalessSource.CONFIG_CSV_CUSTOM_DELIMITER)).strip()
        if len(self.source.config[source.SchemalessSource.CONFIG_CSV_CUSTOM_DELIMITER]) != 1:
            raise click.ClickException(
                f'{self.source.config[source.SchemalessSource.CONFIG_CSV_CUSTOM_DELIMITER]} is not a character')

    def prompt_csv_type(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_CSV_TYPE] = \
            click.prompt('Delimited format type', type=click.Choice(source.SchemalessSource.csv_types),
                         default=default_config.get(source.SchemalessSource.CONFIG_CSV_TYPE,
                                                             source.SchemalessSource.CONFIG_CSV_TYPE_DEFAULT))
        if self.source.config[source.SchemalessSource.CONFIG_CSV_TYPE] == source.SchemalessSource.CONFIG_CSV_TYPE_CUSTOM:
            self.prompt_custom_delimiter(default_config)

    def prompt_csv(self, default_config):
        self.prompt_csv_type(default_config)
        self.change_field_names(default_config)

    def prompt_avro_registry(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_REGISTRY_URLS] = \
            click.prompt('Registry Urls', type=click.STRING,
                         default=default_config.get(source.SchemalessSource.CONFIG_AVRO_SCHEMA_REGISTRY_URLS))
        self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] = \
            click.prompt('Lookup mode', type=click.Choice(source.SchemalessSource.avro_lookup_modes),
                         default=default_config.get(source.SchemalessSource.CONFIG_AVRO_SCHEMA_LOOKUP_MODE))
        if self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] == source.SchemalessSource.AVRO_LOOKUP_ID:
            self.source.config[source.SchemalessSource.CONFIG_AVRO_LOOKUP_ID] = \
                click.prompt('Schema ID', type=click.STRING,
                             default=default_config.get(source.SchemalessSource.CONFIG_AVRO_LOOKUP_ID))
        elif self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_LOOKUP_MODE] == source.SchemalessSource.AVRO_LOOKUP_SUBJECT:
            self.source.config[source.SchemalessSource.CONFIG_AVRO_LOOKUP_SUBJECT] = \
                click.prompt('Schema ID', type=click.STRING,
                             default=default_config.get(source.SchemalessSource.CONFIG_AVRO_LOOKUP_SUBJECT))
        else:
            self.source.config[source.SchemalessSource.CONFIG_KEY_DESERIALIZER] = 'CONFLUENT'
            self.source.config[source.SchemalessSource.CONFIG_VALUE_DESERIALIZER] = 'CONFLUENT'

    def prompt_avro(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_SOURCE] = \
            click.prompt('Schema location', type=click.Choice(source.SchemalessSource.avro_sources),
                         default=default_config.get(source.SchemalessSource.CONFIG_AVRO_SCHEMA_SOURCE))
        if self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_SOURCE] == source.SchemalessSource.AVRO_SCHEMA_SOURCE_INLINE:
            self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_FILE] = \
                click.prompt('Schema file path', type=click.File(),
                             default=default_config.get(source.SchemalessSource.CONFIG_AVRO_SCHEMA_FILE))
            self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA] = json.dumps(
                json.load(self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_FILE]))
        elif self.source.config[source.SchemalessSource.CONFIG_AVRO_SCHEMA_SOURCE] == source.SchemalessSource.AVRO_SCHEMA_SOURCE_REGISTRY:
            self.prompt_avro_registry(default_config)

    @infinite_retry
    def prompt_grok_definition_file(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_GROK_PATTERN_FILE] = \
            click.prompt('Custom grok patterns file path', type=click.STRING,
                         default=default_config.get(source.SchemalessSource.CONFIG_GROK_PATTERN_FILE, ''))
        try:
            self.validator.validate_grok_file()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    def prompt_log(self, default_config):
        records, errors = pipeline.manager.get_sample_records(pipeline.manager.build_test_pipeline(self.source))
        if not records and not errors:
            print('No preview data available')
        elif records:
            print_json(records)
        print(*errors, sep='\n')
        self.prompt_grok_definition_file(default_config)
        self.source.config[source.SchemalessSource.CONFIG_GROK_PATTERN] = \
            click.prompt('Grok pattern', type=click.STRING,
                         default=default_config.get(source.SchemalessSource.CONFIG_GROK_PATTERN))

    def prompt_data_format(self, default_config):
        data_format = click.prompt(
            'Data format',
            type=click.Choice(source.SchemalessSource.data_formats),
            default=default_config.get(
                source.SchemalessSource.CONFIG_DATA_FORMAT,
                source.SchemalessSource.DATA_FORMAT_JSON
            )
        )
        if data_format == source.SchemalessSource.DATA_FORMAT_CSV:
            self.prompt_csv(default_config)
        elif data_format == source.SchemalessSource.DATA_FORMAT_AVRO:
            self.prompt_avro(default_config)
        elif data_format == source.SchemalessSource.DATA_FORMAT_LOG:
            self.prompt_log(default_config)

        self.source.config[source.SchemalessSource.CONFIG_DATA_FORMAT] = data_format
        self.source.set_config(self.source.config)
        return self.source

    def prompt_batch_size(self, default_config):
        self.source.config[source.SchemalessSource.CONFIG_BATCH_SIZE] = \
            click.prompt('Max Batch Size (records)', type=click.IntRange(1),
                         default=default_config.get(source.SchemalessSource.CONFIG_BATCH_SIZE, 1000))
        self.source.config[source.SchemalessSource.CONFIG_BATCH_WAIT_TIME] = \
            click.prompt('Batch Wait Time (ms)', type=click.IntRange(1),
                         default=default_config.get(source.SchemalessSource.CONFIG_BATCH_WAIT_TIME, 1000))

    def change_field_names(self, default_config):
        previous_val = default_config.get(source.SchemalessSource.CONFIG_CSV_MAPPING, {})
        records, errors = pipeline.manager.get_sample_records(pipeline.manager.build_test_pipeline(self.source))
        if not records and not errors:
            print('No preview data available')
        elif records:
            print('Records example:')
            print_dicts(records)
            if previous_val:
                print('Previous mapping:')
                print_dicts(map_keys(records, previous_val))
        print(*errors, sep='\n')
        self.prompt_field_mapping(records, previous_val)

    @infinite_retry
    def prompt_field_mapping(self, records, previous_val):
        new_names = click.prompt(
            'Change fields names (format - key:val,key2:val2,key3:val3)',
            type=click.STRING,
            default=','.join(f'{idx}:{item}' for idx, item in previous_val.items()),
        ).strip()

        if not new_names:
            self.source.config[source.SchemalessSource.CONFIG_CSV_MAPPING] = {}
            print('Saved default mapping')
            return
        data = {}
        for item in new_names.split(','):
            key_val = item.split(':')
            if not key_val or len(key_val) != 2:
                raise click.UsageError('Wrong format. Correct example: `key:val,key2:val2,key3:val3`')
            data[int(key_val[0])] = key_val[1]
        if records:
            print('Current mapping:')
            print_dicts(map_keys(records, data))
            if not click.confirm('Confirm?'):
                raise ValueError('Try again')

        self.source.config[source.SchemalessSource.CONFIG_CSV_MAPPING] = data
