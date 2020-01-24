import click
import json

from .abstract_source import Source, SourceException
from agent.tools import infinite_retry, print_json, if_validation_enabled


class ElasticSource(Source):
    CONFIG_INDEX = 'conf.index'
    CONFIG_MAPPING = 'conf.mapping'
    CONFIG_IS_INCREMENTAL = 'conf.isIncrementalMode'
    CONFIG_QUERY_INTERVAL = 'conf.queryInterval'
    CONFIG_OFFSET_FIELD = 'conf.offsetField'
    CONFIG_INITIAL_OFFSET = 'conf.initialOffset'
    CONFIG_QUERY = 'conf.query'
    CONFIG_CURSOR_TIMEOUT = 'conf.cursorTimeout'
    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_HTTP_URIS = 'conf.httpUris'

    TEST_PIPELINE_NAME = 'test_elastic_asdfs3245'

    VALIDATION_SCHEMA_FILE_NAME = 'elastic.json'

    @infinite_retry
    def prompt_connection(self, default_config):
        self.config[self.CONFIG_HTTP_URIS] = click.prompt('Cluster HTTP URIs',
                                                          type=click.STRING,
                                                          default=default_config.get(
                                                              self.CONFIG_HTTP_URIS)).strip().split(',')

        self.validate_connection()

    def prompt(self, default_config, advanced=False):
        self.config = {}
        self.prompt_connection(default_config)
        self.prompt_index(default_config)
        self.prompt_query(default_config)
        self.prompt_offset_field(default_config)
        self.prompt_initial_offset(default_config)
        self.prompt_interval(default_config)

        return self.config

    def validate(self):
        self.validate_json()
        self.validate_connection()

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return

        print_json(records)

    def prompt_index(self, default_config):
        self.config[self.CONFIG_INDEX] = click.prompt('Index', type=click.STRING,
                                                      default=default_config.get(self.CONFIG_INDEX, ''))

    @infinite_retry
    def prompt_query(self, default_config):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True),
                                                 default=default_config.get('query_file')).strip()
        self.config[self.CONFIG_QUERY] = json.load(self.config['query_file'])

    def prompt_offset_field(self, default_config):
        self.config[self.CONFIG_OFFSET_FIELD] = click.prompt('Offset field', type=click.STRING,
                                                             default=default_config.get(self.CONFIG_OFFSET_FIELD,
                                                                                        'timestamp'))

    def prompt_initial_offset(self, default_config):
        self.config[self.CONFIG_INITIAL_OFFSET] = click.prompt('Initial offset', type=click.STRING,
                                                               default=default_config.get(self.CONFIG_INITIAL_OFFSET,
                                                                                          'now-3d/d'))

    def prompt_interval(self, default_config):
        self.config['query_interval_sec'] = click.prompt('Query interval (seconds)', type=click.IntRange(1),
                                                             default=default_config.get('query_interval_sec', 1))

    def set_config(self, config):
        super().set_config(config)
        self.config[self.CONFIG_QUERY_INTERVAL] = '${' + str(self.config['query_interval_sec']) + ' * SECONDS}'
