import click

from abc import ABC, abstractmethod
from agent import source
from agent.modules import validator
from agent.modules.tools import infinite_retry
from agent.source import Source


class Prompter(ABC):
    def __init__(self, source_: source.Source):
        self.source = source_
        self.validator = source.validator.get_validator(self.source)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass

    def prompt_query_timeout(self, default_config, advanced):
        if advanced:
            self.source.config['query_timeout'] = click.prompt(
                'Query timeout (in seconds)',
                type=click.INT,
                default=default_config.get('query_timeout', self.source.query_timeout)
            )


class APIPrompter(Prompter):
    NAME = ""

    def prompt(self, default_config, advanced=False) -> Source:
        self.prompt_connection(default_config, advanced)
        self.prompt_query_timeout(default_config, advanced)
        return self.source

    @infinite_retry
    def prompt_url(self, default_config):
        url = click.prompt(
            f'{self.NAME} API URL',
            type=click.STRING,
            default=default_config.get(source.APISource.URL)
        ).strip()
        try:
            validator.validate_url_format_with_port(url)
        except validator.ValidationException as e:
            raise click.ClickException(str(e))
        self.source.config[source.APISource.URL] = url

    def prompt_username(self, default_config):
        self.source.config[source.APISource.USERNAME] = click.prompt(
            f'{self.NAME} API username',
            type=click.STRING,
            default=default_config.get(source.APISource.USERNAME, '')
        ).strip()

    def prompt_password(self, default_config):
        self.source.config[source.APISource.PASSWORD] = click.prompt(
            f'{self.NAME} API password',
            type=click.STRING,
            default=default_config.get(source.APISource.PASSWORD, '')
        ).strip()

    def prompt_verify_certificate(self, default_config, advanced):
        verify = click.confirm(
            'Verify ssl certificate?',
            default_config.get(source.APISource.VERIFY_SSL, True)
        ) if advanced else True
        self.source.config[source.APISource.VERIFY_SSL] = verify

    @infinite_retry
    def prompt_connection(self, default_config: dict, advanced: bool):
        self.prompt_url(default_config)
        self.prompt_username(default_config)
        self.prompt_password(default_config)
        self.prompt_verify_certificate(default_config, advanced)
        self.validator.validate_connection()
