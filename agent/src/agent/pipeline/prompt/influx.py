import click

from agent.tools import infinite_retry
from urllib.parse import urljoin
from .base import PromptConfig
from agent import source


class PromptConfigInflux(PromptConfig):
    def set_config(self):
        self.set_measurement_name()
        self.pipeline.source.config['conf.resourceUrl'] = self.get_test_url()
        self.data_preview()
        self.set_value()
        self.set_target_type()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()
        self.set_delay()
        self.set_filtering()

    def get_test_url(self):
        source_config = self.pipeline.source.config
        query = f"select+%2A+from+{self.config['measurement_name']}+limit+{source.manager.MAX_SAMPLE_RECORDS}"
        return urljoin(source_config['host'], f"/query?db={source_config['db']}&epoch=ns&q={query}")

    def set_delay(self):
        self.config['delay'] = click.prompt('Delay', type=click.STRING, default=self.default_config.get('delay', '0s'))
        self.config['interval'] = click.prompt('Interval, seconds', type=click.INT,
                                               default=self.default_config.get('interval', 60))

    @infinite_retry
    def set_value(self):
        self.config['value'] = self.default_config.get('value', {'constant': 1, 'values': []})

        self.config['value']['type'] = 'column'
        default_names = self.config['value'].get('values')
        default_names = ' '.join(default_names) if len(default_names) > 0 else None
        self.config['value']['values'] = click.prompt('Value columns names', type=click.STRING,
                                                      default=default_names).split()
        self.validate_properties_names(self.config['value']['values'], self.pipeline.source.sample_data)
        self.config['value']['constant'] = '1'

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        required = self.config['dimensions'].get('required', [])
        if self.advanced or len(required) > 0:
            self.config['dimensions']['required'] = self.prompt_dimensions('Required dimensions', required)
            self.config['dimensions']['optional'] = click.prompt('Optional dimensions', type=click.STRING,
                                                                 value_proc=lambda x: x.split(),
                                                                 default=self.config['dimensions'].get('optional', []))
        else:
            self.config['dimensions']['required'] = []
            self.config['dimensions']['optional'] = self.prompt_dimensions('Dimensions',
                                                                           self.config['dimensions'].get('optional',
                                                                                                         []))

    def set_filtering(self):
        if self.advanced or self.config.get('filtering', ''):
            self.config['filtering'] = click.prompt('Filtering condition', type=click.STRING,
                                                    default=self.default_config.get('filtering', '')).strip()