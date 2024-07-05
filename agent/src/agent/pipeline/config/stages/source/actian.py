import urllib.parse
from agent import monitoring
from agent.pipeline.config.stages.base import JythonProcessor


class ActianSource(JythonProcessor):
    JYTHON_SCRIPT = 'actian.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractors/actian'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'AGENT_DATA_EXTRACTOR_URL',
                'value': urllib.parse.urljoin(
                    self.pipeline.streamsets.agent_external_url, '/'.join([
                        self.DATA_EXTRACTOR_API_ENDPOINT,
                        '${pipeline:id()}',
                    ])
                )
            },
            {
                'key': 'TIMEOUT',
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
        ]
