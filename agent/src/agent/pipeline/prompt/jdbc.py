import click

from agent.tools import infinite_retry
from .base import PromptConfig


class PromptConfigJDBC(PromptConfig):
    def set_config(self):
        self.set_table()
        self.set_pagination()
        query = f'SELECT * FROM {self.config["table"]}  WHERE {self.config["offset_column"]} > ${{OFFSET}} ORDER BY {self.config["offset_column"]} LIMIT {self.pipeline.source.MAX_SAMPLE_RECORDS}'
        self.pipeline.source.config['query'] = query
        self.pipeline.source.config['offsetColumn'] = self.config['offset_column']
        self.data_preview()
        self.set_values()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()
        self.set_condition()

    @infinite_retry
    def prompt_values(self):
        self.prompt_object('values', 'Value columns with target types. Example - column:counter column2:gauge')
        if not set(self.config['values'].values()).issubset(('counter', 'gauge')):
            raise click.UsageError('Target type should be counter or gauge')
        self.validate_properties_names(self.config['values'].keys())

    def set_table(self):
        self.config['table'] = click.prompt('Table name', type=click.STRING, default=self.default_config.get('table'))

    def set_values(self):
        self.config['count_records'] = int(click.confirm('Count records?',
                                                         default=self.default_config.get('count_records', False)))
        self.prompt_values()

        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value columns or count records flag')

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = self.prompt_property('Timestamp column name',
                                                                self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp column type',
                                                        type=click.Choice(['datetime', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))

    def set_pagination(self):
        self.config['limit'] = click.prompt('Limit', type=click.INT,
                                            default=self.default_config.get('limit', 1000))
        self.config['offset_column'] = self.prompt_property('Unique ID column (must be auto-incremented)',
                                                            self.default_config.get('offset_column', 'id'))
        self.config['initial_offset'] = click.prompt('Collect since (days ago)', type=click.STRING,
                                                     default=self.default_config.get('initial_offset', '3'))

    def set_condition(self):
        if self.advanced:
            self.config['condition'] = click.prompt('Condition', type=click.STRING,
                                                    default=self.default_config.get('condition'))
