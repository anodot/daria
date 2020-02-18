import click
from .json import PromptConfigJson


class PromptConfigElastic(PromptConfigJson):
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

    def prompt_query(self):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True, dir_okay=False),
                                                 default=self.default_config.get('query_file'))
        with open(self.config['query_file'], 'r') as f:
            self.pipeline.source.config[self.pipeline.source.CONFIG_QUERY] = f.read()
