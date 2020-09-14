import click

from .schemaless import PromptConfigSchemaless
from agent import source
from agent.modules.tools import infinite_retry
from agent.pipeline.elastic import query_validator


class PromptConfigElastic(PromptConfigSchemaless):
    timestamp_types = ['string', 'unix', 'unix_ms']

    def prompt_config(self):
        self.prompt_query()
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

    @infinite_retry
    def prompt_query(self):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True, dir_okay=False),
                                                 default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as f:
            query = f.read()
            offset_field = self.pipeline.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD]
            errors = query_validator.get_errors(query, offset_field)
            if errors:
                raise click.ClickException(errors)
            self.pipeline.source.config[source.ElasticSource.CONFIG_QUERY] = query
