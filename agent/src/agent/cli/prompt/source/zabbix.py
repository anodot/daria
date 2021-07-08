from .base import APIPrompter
from agent import source


class ZabbixPrompter(APIPrompter):
    NAME = "Zabbix"

    def prompt_username(self, default_config):
        super(ZabbixPrompter, self).prompt_username(default_config)
        # hack to keep backward compatibility
        self.source.config[source.ZabbixSource.USER] = self.source.config.pop(source.APISource.USERNAME)
