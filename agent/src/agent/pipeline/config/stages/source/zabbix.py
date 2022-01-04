import os
import json

from agent import source
from agent.pipeline.config.stages.base import JythonSource


class ZabbixScript(JythonSource):
    JYTHON_SCRIPT = 'zabbix.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self.pipeline.source.config[source.ZabbixSource.URL]
            },
            {
                'key': 'USER',
                'value': self.pipeline.source.config[source.ZabbixSource.USER]
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config[source.ZabbixSource.PASSWORD]
            },
            {
                'key': 'QUERY',
                'value': json.dumps(self.pipeline.query)
            },
            {
                'key': 'QUERY_TIMEOUT',
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                'key': 'LOG_EVERYTHING',
                'value': '1' if self.pipeline.log_everything else ''
            },
            {
                'key': 'INITIAL_TIMESTAMP',
                'value': str(int(self.get_initial_timestamp().timestamp()))
            },
            {
                'key': 'INTERVAL',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'ITEMS_BATCH_SIZE',
                'value': str(self.pipeline.batch_size)
            },
            {
                'key': 'HISTORIES_BATCH_SIZE',
                'value': str(self.pipeline.histories_batch_size)
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
            },
        ]


class TestZabbixScript(JythonSource):
    JYTHON_SCRIPT = 'zabbix.py'
    JYTHON_SCRIPTS_PATH = os.path.join(JythonSource.JYTHON_SCRIPTS_PATH, 'test_pipelines')

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self.pipeline.source.config[source.ZabbixSource.URL]
            },
            {
                'key': 'USER',
                'value': self.pipeline.source.config[source.ZabbixSource.USER]
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config[source.ZabbixSource.PASSWORD]
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
            },
        ]
