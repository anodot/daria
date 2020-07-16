import click

from agent import source
from agent.pipeline.prompt import PromptConfig
from agent.tools import infinite_retry


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        # todo базовая авторизация
        self.prompt_query()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.set_static_properties()
        self.set_tags()

    @infinite_retry
    def prompt_url(self):
        url = click.prompt('VictoriaMetrics URL', type=click.STRING, default=self.default_config.get('url'))
        if not source.validator.is_valid_url(url):
            raise click.ClickException('URL has invalid format, please specify both the hostname and protocol')
        self.config['url'] = url

    def prompt_username(self):
        self.config['username'] = click.prompt('VictoriaMetrics username', type=click.STRING,
                                               default=self.default_config.get('url'))

    def prompt_password(self):
        self.config['password'] = click.prompt('VictoriaMetrics password', type=click.STRING,
                                               default=self.default_config.get('url'))

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('metrics'))

    def prompt_days_to_backfill(self):
        self.config['days_to_backfill'] = \
            int(click.prompt('Collect since (days ago, collect all if empty)', type=click.STRING,
                             default=self.default_config.get('days_to_backfill')))

    def prompt_interval(self):
        self.config['interval'] = click.prompt('Query interval (in seconds)', type=click.INT,
                                               default=self.default_config.get('initial_offset'))
