import json
import click

from agent.cli.prompt.pipeline.schemaless import SchemalessPrompter
from agent.modules.tools import infinite_retry


class ZabbixPrompter(SchemalessPrompter):
    def prompt_config(self):
        self.prompt_query_file()
        self.prompt_batch_sizes()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_dimensions()
        self.prompt_delay()
        self.set_transform()
        self.set_static_dimensions()
        self.set_tags()
        # todo code duplicate
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.config['timestamp']['name'] = 'clock'

    @infinite_retry
    def prompt_batch_sizes(self):
        items_batch_size = self.default_config.get('batch_size', 1000)
        histories_batch_size = self.default_config.get('histories_batch_size', 100)
        if self.advanced:
            items_batch_size = click.prompt('Items batch size', type=click.INT, default=items_batch_size)
            histories_batch_size = click.prompt('Histories batch size', type=click.INT, default=histories_batch_size)
        self.config['batch_size'] = items_batch_size
        self.config['histories_batch_size'] = histories_batch_size

    @infinite_retry
    def set_values(self):
        self.config['static_what'] = False
        self.config['count_records'] = \
            int(click.confirm('Count records?', default=self.default_config.get('count_records', False)))
        if self.config['count_records']:
            self.config['count_records_measurement_name'] = click.prompt(
                'Measurement name',
                type=click.STRING,
                default=self.default_config.get('count_records_measurement_name')
            )
        self.prompt_values()
        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value properties or count records flag')

    @infinite_retry
    def prompt_query_file(self):
        self.config['query_file'] = click.prompt('File with query params', type=click.STRING, default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as fp:
            self.config['query'] = json.load(fp)

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))
