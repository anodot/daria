import click

from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source
from agent.modules import validator


class SolarWindsPrompter(Prompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)

    @infinite_retry
    def prompt_connection(self, default_config):
        # todo duplicate with Victoria?
        self.prompt_url(default_config)
        self.prompt_username(default_config)
        self.prompt_password(default_config)

        self.validator.validate_connection()

    @infinite_retry
    def prompt_url(self, default_config):
        url = click.prompt('SolarWinds API URL', type=click.STRING,
                           default=default_config.get(source.SolarWindsSource.URL)).strip()
        try:
            validator.validate_url_format_with_port(url)
        except validator.ValidationException as e:
            raise click.ClickException(str(e))
        self.source.config[source.VictoriaMetricsSource.URL] = url

    def prompt_username(self, default_config):
        self.source.config['username'] = click.prompt('VictoriaMetrics username', type=click.STRING,
                                                      default=default_config.get('username', '')).strip()

    def prompt_password(self, default_config):
        self.source.config['password'] = click.prompt('VictoriaMetrics password', type=click.STRING,
                                                      default=default_config.get('password', '')).strip()
