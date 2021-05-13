from agent.source import Source
from .base import APIPrompter
from agent.modules.tools import infinite_retry


class SolarWindsPrompter(APIPrompter):
    def prompt(self, default_config, advanced=False) -> Source:
        self.prompt_connection(default_config)
        self.prompt_query_timeout(default_config, advanced)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_url('SolarWinds API URL', default_config)
        self.prompt_username('SolarWinds API username', default_config)
        self.prompt_password('SolarWinds API password', default_config)

        self.validator.validate_connection()
