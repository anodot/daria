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
