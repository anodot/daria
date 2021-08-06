import click

from .base import Prompter


class InfluxPrompter(Prompter):
    def prompt_config(self):
        self.set_measurement_name()
        # todo what if delete it?
        # self.pipeline.source.config['conf.resourceUrl'] = self.get_test_url()
        self.data_preview()
        self.prompt_values()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.set_delay()
        self.set_filtering()
        self.set_uses_schema()
        self.config['timestamp'] = {
            'type': 'unix_ms',
            'name': 'time',
        }

    # todo delete?
    # def get_test_url(self):
    #     source_config = self.pipeline.source.config
    #     query = f"select+%2A+from+{self.config['measurement_name']}+limit+{pipeline.manager.MAX_SAMPLE_RECORDS}"
    #     if self.pipeline.source.is_v2():
    #         return urljoin(source_config['host'], f"/query?database={source_config['bucket']}&epoch=ns&q={query}")
    #     return urljoin(source_config['host'], f"/query?db={source_config['db']}&epoch=ns&q={query}")

    def set_delay(self):
        self.config['delay'] = click.prompt('Delay', type=click.STRING, default=self.default_config.get('delay', '0s'))
        self.config['interval'] = click.prompt('Interval, seconds', type=click.INT,
                                               default=self.default_config.get('interval', 60))

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        required = self.config['dimensions'].get('required', [])
        if self.advanced or len(required) > 0:
            self.config['dimensions']['required'] = self.prompt_dimensions('Required dimensions', required)
            self.config['dimensions']['optional'] = click.prompt(
                'Optional dimensions', type=click.STRING,
                value_proc=lambda x: x.split(),
                default=self.config['dimensions'].get('optional', [])
            )
        else:
            self.config['dimensions']['required'] = []
            self.config['dimensions']['optional'] = \
                self.prompt_dimensions('Dimensions', self.config['dimensions'].get('optional', []))

    def set_filtering(self):
        if self.advanced or self.config.get('filtering', ''):
            self.config['filtering'] = click.prompt(
                'Filtering condition',
                type=click.STRING,
                default=self.default_config.get('filtering', '')
            ).strip()


class Influx2Prompter(InfluxPrompter):
    def prompt_config(self):
        self.prompt_query_type()
        self.set_measurement_name()
        self.data_preview()
        self.prompt_values()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.set_delay()
        self.set_filtering()
        # todo make a class to set defaults
        self.config['uses_schema'] = True
        self.config['timestamp'] = {
            'type': 'unix_ms',
            'name': '_time',
        }

    # todo same for file, add to test input
    def prompt_query_type(self):
        self.config['query_type'] = click.prompt(
            'Query type',
            # todo constants
            type=click.Choice(['InfluxQL', 'Flux']),
            default=self.default_config.get('query_type', 'InfluxQL')
        )
