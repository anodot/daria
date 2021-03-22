import click

from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source


class SagePrompter(Prompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_url(default_config)
        self.prompt_token(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_url(self, default_config):
        self.source.config[source.SageSource.URL] = \
            click.prompt('Sage API URL', type=click.STRING, default=default_config.get(source.SageSource.URL)).strip()
        try:
            self.validator.validate_url()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    @infinite_retry
    def prompt_token(self, default_config):
        self.source.config[source.SageSource.TOKEN] = \
            click.prompt('Sage API token', type=click.STRING, default=default_config.get(source.SageSource.TOKEN)).strip()
        self.validator.validate_token()
