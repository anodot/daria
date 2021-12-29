from agent.pipeline.config.stages.base import JythonDataExtractorSource


class SNMP(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'snmp.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'snmp'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'SNMP_SOURCE_URL',
                'value': self._get_source_url()
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'SCHEMA_ID',
                'value': str(self.pipeline.get_schema_id())
            },
        ]


class SNMPRaw(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'snmp_raw.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'snmp/raw/'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'SNMP_SOURCE_URL',
                'value': self._get_source_url()
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
        ]
