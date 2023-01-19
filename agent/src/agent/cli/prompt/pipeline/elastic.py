import click

from .schemaless import SchemalessPrompter
from agent import source
from agent.modules.tools import infinite_retry
from agent.pipeline.validators import elastic_query


class ElasticPrompter(SchemalessPrompter):
    timestamp_types = ['string', 'unix', 'unix_ms']

    def prompt_config(self):
        self.prompt_query()
        self.data_preview()
        self.set_values()
        self.prompt_measurement_names()
        self.prompt_timestamp()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()

    @infinite_retry
    def prompt_query(self):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True, dir_okay=False),
                                                 default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as f:
            query = f.read()
            offset_field = self.pipeline.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD]
            errors = elastic_query.get_errors(query, offset_field, self.pipeline.uses_schema())
            if errors:
                raise click.ClickException(errors)

            self.config['query'] = query
