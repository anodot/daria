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
        self.prompt_connection(default_config, self.NAME)
        self.prompt_verify_certificate(default_config, advanced)
        self.prompt_query_timeout(default_config, advanced)
        return self.source

    @infinite_retry
    def prompt_url(self, prompt_text: str, default_config):
        url = click.prompt(
            prompt_text,
            type=click.STRING,
            default=default_config.get(source.APISource.URL)
        ).strip()
        try:
            validator.validate_url_format_with_port(url)
        except validator.ValidationException as e:
            raise click.ClickException(str(e))
        self.source.config[source.APISource.URL] = url

    def prompt_username(self, prompt_text: str, default_config):
        self.source.config['username'] = click.prompt(
            prompt_text,
            type=click.STRING,
            default=default_config.get('username', '')
        ).strip()

    def prompt_password(self, prompt_text: str, default_config):
        self.source.config['password'] = click.prompt(
            prompt_text,
            type=click.STRING,
            default=default_config.get('password', '')
        ).strip()

    def prompt_verify_certificate(self, default_config, advanced):
        verify = click.confirm('Verify ssl certificate?', default_config.get('verify_ssl', True)) if advanced else True
        self.source.config['verify_ssl'] = verify

    @infinite_retry
    def prompt_connection(self, default_config: dict, name: str):
        self.prompt_url(f'{name} API URL', default_config)
        self.prompt_username(f'{name} API username', default_config)
        self.prompt_password(f'{name} API password', default_config)
        self.validator.validate_connection()
