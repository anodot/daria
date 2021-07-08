import json

from agent import source
from agent.pipeline.config.stages.base import Stage


class ZabbixScript(Stage):
    JYTHON_SCRIPT = 'zabbix.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'URL', 'value': self.pipeline.source.config[source.ZabbixSource.URL]},
                    {'key': 'USER', 'value': self.pipeline.source.config[source.ZabbixSource.USER]},
                    {'key': 'PASSWORD', 'value': self.pipeline.source.config[source.ZabbixSource.PASSWORD]},
                    {'key': 'QUERY', 'value': json.dumps(self.pipeline.query)},
                    {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.query_timeout)},
                    {'key': 'INITIAL_TIMESTAMP', 'value': str(int(self.get_initial_timestamp().timestamp()))},
                    {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_MINUTES', 'value': str(self.pipeline.delay)},
                    {'key': 'ITEMS_BATCH_SIZE', 'value': str(self.pipeline.batch_size)},
                    {'key': 'HISTORIES_BATCH_SIZE', 'value': str(self.pipeline.histories_batch_size)},
                ],
                'script': f.read(),
            }
