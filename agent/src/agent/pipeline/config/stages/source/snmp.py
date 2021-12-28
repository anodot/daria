from agent.pipeline.config.stages.base import JythonDataExtractorSource


class SNMP(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'snmp.py'
    DATA_EXTRACTOR_API_PATH = 'data_extractors/snmp/'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
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
                ],
                'script': f.read(),
            }


class SNMPRaw(JythonDataExtractorSource):
    DATA_EXTRACTOR_API_PATH = 'data_extractors/snmp/raw/'

    def get_config(self) -> dict:
        return {
            'scriptConf.params': [
                {
                    'key': 'SNMP_SOURCE_URL',
                    'value': self._get_source_url()
                },
                {
                    'key': 'INTERVAL_IN_SECONDS',
                    'value': str(self.pipeline.interval)
                },
            ]
        }
