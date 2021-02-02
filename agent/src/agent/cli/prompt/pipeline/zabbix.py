import json
import click

from agent.cli.prompt.pipeline.schemaless import PromptConfigSchemaless
from agent.modules.tools import infinite_retry


class PromptConfigZabbix(PromptConfigSchemaless):
    def prompt_config(self):
        self.prompt_query_file()
        # todo it asks for count props, do we need it?
        self.set_values()
        self.set_measurement_names()
        self.set_dimensions()
        self.prompt_interval()
        self.prompt_days_to_backfill()
        self.prompt_delay()
        self.set_transform()
        self.set_tags()
        # todo code duplicate
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.config['timestamp']['name'] = 'clock'

    @infinite_retry
    def prompt_query_file(self):
        self.config['query_file'] = click.prompt('File with query params', type=click.STRING, default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as fp:
            self.config['query'] = json.load(fp)

    # todo use mixins for such methods?
    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))
