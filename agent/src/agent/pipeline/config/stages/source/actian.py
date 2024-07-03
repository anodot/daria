from agent import monitoring
from agent.pipeline.config.stages.base import JythonDataExtractorSource


class ActianScript(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'actian.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractors/actian'

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
                'key': 'DELAY_IN_SECONDS',
                'value': self.pipeline.config.get('delay', '0')
            },
        ]
