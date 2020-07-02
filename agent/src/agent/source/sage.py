import click

from .abstract_source import Source
from agent.tools import infinite_retry, is_url, print_dicts, if_validation_enabled


class SageSource(Source):
    VALIDATION_SCHEMA_FILE_NAME = 'sage.json'
    TEST_PIPELINE_FILENAME = 'test_sage_jfhdkj'

    URL = 'url'
    TOKEN = 'token'

    def validate_url(self):
        if not is_url(self.config[self.URL]):
            raise click.UsageError('Wrong url format. Correct format is `scheme://host:port`')
        # TODO: check simple request

    @infinite_retry
    def prompt_url(self, default_config):
        self.config[self.URL] = click.prompt('Sage API URL',
                                             type=click.STRING,
                                             default=default_config.get(self.URL)).strip()
        self.validate_url()

    def validate_token(self):
        # TODO: check token
        pass

    @infinite_retry
    def prompt_token(self, default_config):
        self.config[self.TOKEN] = click.prompt('Sage API token',
                                               type=click.STRING,
                                               default=default_config.get(self.TOKEN)).strip()
        self.validate_token()

    def prompt(self, default_config, advanced=False):
        self.config = dict()
        self.prompt_url(default_config)
        self.prompt_token(default_config)

        return self.config

    def validate(self):
        self.validate_json()
        self.validate_url()
        self.validate_token()

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return

        print_dicts(records)
