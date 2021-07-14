import urllib.parse

from agent.modules.time import Interval
from agent.pipeline.config.stages.base import Stage


class SNMPInterval(Interval):
    VALUES = [Interval.MIN_1, Interval.MIN_5, Interval.HOUR_1]


class SNMP(Stage):
    JYTHON_SCRIPT = 'snmp.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'SNMP_SOURCE_URL', 'value': self._get_snmp_source_url()},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': self._get_interval()},
                ],
                'script': f.read(),
            }

    def _get_snmp_source_url(self) -> str:
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url,
            'data_extractor/snmp/${pipeline:id()}'
        )

    def _get_interval(self) -> str:
        return str(SNMPInterval(self.pipeline.interval).total_seconds())
