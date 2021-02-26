import click

from agent.modules import validator
from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source


class ZabbixPrompter(Prompter):
    @infinite_retry
    def prompt(self, default_config, advanced=False):
        self.prompt_url(default_config)
        self.prompt_username(default_config)
        self.prompt_password(default_config)
        self.prompt_query_timeout(default_config, advanced)
        self.validator.validate_connection()
        return self.source

    @infinite_retry
    def prompt_url(self, default_config):
        url = click.prompt('Zabbix URL', type=click.STRING, default=default_config.get(source.ZabbixSource.URL)).strip()
        validator.validate_url_format_with_port(url)
        self.source.config[source.ZabbixSource.URL] = url

    def prompt_username(self, default_config):
        self.source.config[source.ZabbixSource.USER] = click.prompt(
            'Zabbix user',
            type=click.STRING,
            default=default_config.get(source.ZabbixSource.USER, '')
        ).strip()

    def prompt_password(self, default_config):
        self.source.config[source.ZabbixSource.PASSWORD] = click.prompt(
            'Zabbix password',
            type=click.STRING,
            default=default_config.get(source.ZabbixSource.PASSWORD, '')
        ).strip()
