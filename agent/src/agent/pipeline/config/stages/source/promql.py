import os

from agent import source, monitoring
from agent.pipeline.config.stages.base import JythonSource


class PromQLScript(JythonSource):
    JYTHON_SCRIPT = 'promql.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self.pipeline.source.config[source.PromQLSource.URL]
            },
            {
                'key': 'USERNAME',
                'value': self.pipeline.source.config.get(source.PromQLSource.USERNAME, '')
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config.get(source.PromQLSource.PASSWORD, '')
            },
            {
                'key': 'QUERY',
                'value': self.pipeline.config['query']
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
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
            },
            {
                'key': 'QUERY_TIMEOUT',
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                'key': 'AGGREGATED_METRIC_NAME',
                'value': str(self.pipeline.config.get('aggregated_metric_name'))
            },
            {
                'key': 'HEADERS',
                'value': self.pipeline.config.get('request_headers', {})
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
        ]


class TestPromQLScript(JythonSource):
    JYTHON_SCRIPT = 'promql.py'
    JYTHON_SCRIPTS_DIR = os.path.join(JythonSource.JYTHON_SCRIPTS_DIR, 'test_pipelines')

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self.pipeline.source.config[source.PromQLSource.URL]
            },
            {
                'key': 'USERNAME',
                'value': self.pipeline.source.config.get(source.PromQLSource.USERNAME, '')
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config.get(source.PromQLSource.PASSWORD, '')
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
            },
            {
                'key': 'REQUEST_TIMEOUT',
                'value': 10
            },
        ]
