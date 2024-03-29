import click

from .schemaless import SchemalessPrompter


class SagePrompter(SchemalessPrompter):

    def prompt_config(self):
        self.set_query()
        self.prompt_delay()
        self.prompt_interval()
        self.prompt_days_to_backfill()
        # self.data_preview()
        self.set_values()
        self.prompt_measurement_names()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()

    def set_query(self):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True, dir_okay=False),
                                                 default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as f:
            self.config['query'] = f.read()

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions',
                                                           default_value=self.default_config.get('dimensions', []))
