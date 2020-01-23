import click

from .base import PromptConfig
from agent.tools import infinite_retry


class PromptConfigMongo(PromptConfig):
    def set_config(self):
        self.data_preview()
        self.set_measurement_name()
        self.set_value()
        self.set_target_type()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

    @infinite_retry
    def prompt_value(self):
        self.config['value']['value'] = click.prompt('Value property name', type=click.STRING,
                                                     default=self.config['value'].get('value'))
        self.validate_properties_names([self.config['value']['value']])

    def set_value(self):
        self.config['value'] = self.default_config.get('value', {})
        if self.advanced or self.config['value'].get('type') == 'constant':
            self.config['value']['value'] = click.prompt('Value (property name or constant value)', type=click.STRING,
                                                         default=self.config['value'].get('value'))
            self.config['value']['type'] = click.prompt('Value type', type=click.Choice(['property', 'constant']),
                                                        default=self.config['value'].get('type'))
        else:
            self.config['value']['type'] = 'property'
            self.prompt_value()