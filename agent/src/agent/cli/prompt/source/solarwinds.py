from agent.source import Source
from .base import APIPrompter
from agent.modules.tools import infinite_retry
from agent import source


class SolarWindsPrompter(APIPrompter):
    def prompt(self, default_config, advanced=False) -> Source:
        self.prompt_connection(default_config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_url(default_config)
        self.prompt_username('SolarWinds API username', default_config)
        self.prompt_password('SolarWinds API password', default_config)

        self.validator.validate_connection()

    @infinite_retry
    def prompt_url(self, default_config):
        super().prompt_url('SolarWinds API URL', default_config)
        if self.source.config[source.SolarWindsSource.URL][-1] == '/':
            self.source.config[source.SolarWindsSource.URL] = self.source.config[source.SolarWindsSource.URL][:-1]
