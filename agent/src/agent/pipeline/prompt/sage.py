import click

from .schemaless import PromptConfigSchemaless


class PromptConfigSage(PromptConfigSchemaless):

    def set_config(self):
        self.set_query()
        self.set_delay()
        self.set_interval()
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

    def set_query(self):
        self.config['query_file'] = click.prompt('Query file path', type=click.Path(exists=True, dir_okay=False),
                                                 default=self.default_config.get('query_file'))

    def set_delay(self):
        self.config['delay'] = click.prompt('Delay, minutes', type=click.INT,
                                            default=self.default_config.get('delay', 0))

    def set_interval(self):
        self.config['interval'] = click.prompt('Interval, minutes', type=click.INT,
                                               default=self.default_config.get('interval', 5))
