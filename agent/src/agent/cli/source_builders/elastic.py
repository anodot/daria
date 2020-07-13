import click

from .abstract_builder import Builder
from agent.tools import infinite_retry, print_json, if_validation_enabled
from agent import source


class ElasticSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_index(default_config)
        self.prompt_offset_field(default_config)
        self.prompt_initial_offset(default_config)
        self.prompt_interval(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        default_uris = default_config.get(source.ElasticSource.CONFIG_HTTP_URIS)
        if default_uris:
            default_uris = ','.join(default_uris)
        self.source.config[source.ElasticSource.CONFIG_HTTP_URIS] = click.prompt('Cluster HTTP URIs', type=click.STRING,
                                                                                 default=default_uris).strip().split(
            ',')
        self.validator.validate_connection()
        print('Successfully connected to the source')

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return
        print_json(records)

    def prompt_index(self, default_config):
        self.source.config[source.ElasticSource.CONFIG_INDEX] = \
            click.prompt('Index', type=click.STRING, default=default_config.get(source.ElasticSource.CONFIG_INDEX, ''))

    def prompt_offset_field(self, default_config):
        self.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD] = click.prompt(
            'Offset field (Elasticsearch Date field)',
            type=click.STRING,
            default=default_config.get(source.ElasticSource.CONFIG_OFFSET_FIELD,
                                       'timestamp'))

    def prompt_initial_offset(self, default_config):
        self.source.config[source.ElasticSource.CONFIG_INITIAL_OFFSET] = \
            click.prompt('Initial offset', type=click.STRING,
                         default=default_config.get(source.ElasticSource.CONFIG_INITIAL_OFFSET, 'now'))

    def prompt_interval(self, default_config):
        self.source.config['query_interval_sec'] = click.prompt('Query interval (seconds)', type=click.IntRange(1),
                                                                default=default_config.get('query_interval_sec', 1))
