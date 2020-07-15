import click

from .abstract_builder import Builder
from agent.tools import infinite_retry
from agent import source


class VictoriaSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_url(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_url(self, default_config):
        self.source.config[source.VictoriaMetricsSource.URL] = \
            click.prompt('VictoriaMetrics API URL', type=click.STRING,
                         default=default_config.get(source.VictoriaMetricsSource.URL)).strip()
        try:
            self.validator.validate_url()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    def prompt_username(self, default_config):
        self.source.config[source.VictoriaMetricsSource.USERNAME] = \
            click.prompt('VictoriaMetrics username', type=click.STRING,
                         default=default_config.get(source.VictoriaMetricsSource.USERNAME)).strip()

    def prompt_password(self, default_config):
        self.source.config[source.VictoriaMetricsSource.PASSWORD] = \
            click.prompt('VictoriaMetrics password', type=click.STRING,
                         default=default_config.get(source.VictoriaMetricsSource.PASSWORD)).strip()
