from agent.cli.prompt.source.base import APIPrompter
from agent.modules.tools import infinite_retry


class VictoriaPrompter(APIPrompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_verify_certificate(default_config, advanced)
        self.prompt_query_timeout(default_config, advanced)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_url('VictoriaMetrics API URL', default_config)
        self.prompt_username('VictoriaMetrics username', default_config)
        self.prompt_password('VictoriaMetrics password', default_config)
        self.validator.validate_connection()
