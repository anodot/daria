import click

from .abstract_builder import Builder
from agent.tools import infinite_retry
from agent import source


class VictoriaSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_url(default_config)
        self.prompt_username(default_config)
        self.prompt_password(default_config)
        self.validator.validate_connection()

    @infinite_retry
    def prompt_url(self, default_config):
        url = click.prompt('VictoriaMetrics API URL', type=click.STRING,
                           default=default_config.get(source.VictoriaMetricsSource.URL)).strip()
        if not source.validator.is_valid_url(url):
            raise click.ClickException('URL has invalid format, please specify both the hostname and protocol')
        self.source.config[source.VictoriaMetricsSource.URL] = url

    def prompt_username(self, default_config):
        self.source.config['username'] = click.prompt('VictoriaMetrics username', type=click.STRING,
                                                      default=default_config.get('username', '')).strip()

    def prompt_password(self, default_config):
        self.source.config['password'] = click.prompt('VictoriaMetrics password', type=click.STRING,
                                                      default=default_config.get('password', '')).strip()
