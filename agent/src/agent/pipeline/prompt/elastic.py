import click
import re

from .schemaless import PromptConfigSchemaless
from agent.source import ElasticSource
from agent.tools import infinite_retry


class PromptConfigElastic(PromptConfigSchemaless):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']

    def set_config(self):
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
            offset_field = self.pipeline.source.config[ElasticSource.CONFIG_OFFSET_FIELD]
            if not is_valid_timestamp(query, offset_field):
                raise click.ClickException(f'The query should have ascending ordering by {offset_field}')
            if not is_valid_offset(query):
                raise click.ClickException('Please use ${OFFSET} with a gt condition (not gte)')
            self.pipeline.source.config[self.pipeline.source.CONFIG_QUERY] = query


def is_valid_timestamp(query: str, offset_field: str) -> bool:
    regexp = re.compile(rf'"sort"[\s\S]*"{offset_field}"[\s\S]*"order"[\s\S]*"asc"')
    if regexp.search(query):
        return True
    return False


def is_valid_offset(query: str) -> bool:
    regexp = re.compile(r'"gt"[\s\S]*\${OFFSET}')
    if regexp.search(query):
        return True
    return False
