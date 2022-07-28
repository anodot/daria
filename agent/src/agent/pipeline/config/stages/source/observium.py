from agent import monitoring
from agent.pipeline.config.stages.base import JythonDataExtractorSource


class ObserviumScript(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'observium.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractors/observium'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'AGENT_DATA_EXTRACTOR_URL',
                'value': self._get_source_url()
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'BUCKET_SIZE',
                'value': self._get_bucket_size(),
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
            {
                'key': 'OBSERVIUM_STEP_IN_SECONDS',
                'value': str(self.pipeline.config.get('step', '300'))
            },
            {
                'key': 'DELAY_IN_SECONDS',
                'value': str(self.pipeline.config.get('delay', '0'))
            },
        ]

    def _get_bucket_size(self) -> str:
        if self.pipeline.interval == 60:
            return '1m'
        elif self.pipeline.interval == 300:
            return '5m'
        elif self.pipeline.interval == 3600:
            return '1h'
        else:
            raise Exception(f'Invalid interval provided for Observium: {self.pipeline.interval}')
