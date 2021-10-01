import urllib.parse

from functools import reduce
from agent.pipeline.config.stages.base import Stage


class SNMP(Stage):
    JYTHON_SCRIPT = 'snmp.py'
    DATA_EXTRACTOR_API_PATH = 'data_extractor/snmp/'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'SNMP_SOURCE_URL', 'value': self._get_snmp_source_url()},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'SCHEMA_ID', 'value': str(self.pipeline.get_schema_id())},
                ],
                'script': f.read(),
            }

    def _get_snmp_source_url(self) -> str:
        return reduce(urllib.parse.urljoin, [
            self.pipeline.streamsets.agent_external_url,
            self.DATA_EXTRACTOR_API_PATH,
            '${pipeline:id()}'
        ])


class SNMPRaw(SNMP):
    DATA_EXTRACTOR_API_PATH = 'data_extractor/snmp/raw/'

    def get_config(self) -> dict:
        return {
            'scriptConf.params': [
                {'key': 'SNMP_SOURCE_URL', 'value': self._get_snmp_source_url()},
                {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
            ]
        }
