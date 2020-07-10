import click

from .abstract_builder import Builder
from agent.tools import infinite_retry, is_url, print_dicts, if_validation_enabled
from agent import source


class SageSource(Builder):
    URL = 'url'
    TOKEN = 'token'

    def prompt(self, default_config, advanced=False):
        self.prompt_url(default_config)
        self.prompt_token(default_config)
        self.source.set_config(self.source.config)
        return self.source

    def validate(self):
        source.validator.validate_json(self.source)
        self.validate_url()
        self.validate_token()

    @if_validation_enabled
    def validate_url(self):
        if not is_url(self.source.config[self.URL]):
            raise click.UsageError('Wrong url format. Correct format is `scheme://host:port`')
        # TODO: check simple request

    @infinite_retry
    def prompt_url(self, default_config):
        self.source.config[self.URL] = \
            click.prompt('Sage API URL', type=click.STRING, default=default_config.get(self.URL)).strip()
        self.validate_url()

    def validate_token(self):
        # TODO: check token
        pass

    @infinite_retry
    def prompt_token(self, default_config):
        self.source.config[self.TOKEN] = \
            click.prompt('Sage API token', type=click.STRING, default=default_config.get(self.TOKEN)).strip()
        self.validate_token()

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return
        print_dicts(records)
