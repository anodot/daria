import click

from .schemaless import PromptConfigSchemaless


class PromptConfigSage(PromptConfigSchemaless):

    def set_config(self):
        self.set_query()
        self.set_delay()
        self.set_interval()
        self.set_number_of_days_to_backfill()
        # self.data_preview()
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

    def set_number_of_days_to_backfill(self):
        self.config['days_to_backfill'] = click.prompt('Number of days to backfill', type=click.INT,
                                                       default=self.default_config.get('days_to_backfill', 0))

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions',
                                                           default_value=self.default_config.get('dimensions', []))
