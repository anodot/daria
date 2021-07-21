import urllib.parse

from agent.pipeline.config.stages.base import Stage


class SNMP(Stage):
    JYTHON_SCRIPT = 'snmp.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'SNMP_SOURCE_URL', 'value': self._get_snmp_source_url()},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                ],
                'script': f.read(),
            }

    def _get_snmp_source_url(self) -> str:
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url,
            'data_extractor/snmp/${pipeline:id()}'
        )
