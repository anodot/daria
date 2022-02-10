import os

from urllib.parse import urljoin
from agent import monitoring
from agent.pipeline.config.stages.influx import InfluxScript
from agent.pipeline.config.stages.base import JythonSource

TIMESTAMP_CONDITION = '{TIMESTAMP_CONDITION}'


class Influx2Source(InfluxScript):
    JYTHON_SCRIPT = 'influx2.py'

    def _get_script_params(self) -> list[dict]:
        params = super()._get_script_params()
        params.extend([
            {
                'key': 'URL',
                'value': self._get_url()
            },
            {
                'key': 'HEADERS',
                'value': self._get_headers()
            },
            {
                'key': 'QUERY',
                'value': self._get_query()
            },
            {
                'key': 'TIMEOUT',
                'value': self.pipeline.source.query_timeout
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
        ])
        return params

    def _get_url(self) -> str:
        return urljoin(self.pipeline.source.config['host'], f'/api/v2/query?org={self.pipeline.source.config["org"]}')

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Token {self.pipeline.source.config["token"]}',
            'Accept': 'application/csv',
            'Content-type': 'application/vnd.flux',
        }

    def _get_query(self) -> str:
        query = self.pipeline.query or \
               f'from(bucket:"{self.pipeline.source.config["bucket"]}") ' \
               '|> {TIMESTAMP_CONDITION} ' \
               f'|> filter(fn: (r) => {self._get_filter_condition()}")'
        return query.replace(TIMESTAMP_CONDITION, 'range(start: {}, stop: {})')

    def _get_filter_condition(self) -> str:
        filter_condition = f'r._measurement == "{self.pipeline.config["measurement_name"]}'
        custom_filtering = self.pipeline.config.get('filtering')
        if custom_filtering:
            filter_condition += f' and {custom_filtering}'
        return filter_condition


class TestInflux2Source(JythonSource):
    JYTHON_SCRIPT = 'influx2.py'
    JYTHON_SCRIPTS_DIR = os.path.join(JythonSource.JYTHON_SCRIPTS_DIR, 'test_pipelines')

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self._get_url()
            },
            {
                'key': 'HEADERS',
                'value': self._get_headers()
            },
            {
                'key': 'REQUEST_TIMEOUT',
                'value': 10
            },
        ]

    def _get_url(self) -> str:
        return urljoin(self.pipeline.source.config['host'], '/api/v2/buckets')

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Token {self.pipeline.source.config["token"]}',
            'Accept': 'application/csv',
            'Content-type': 'application/vnd.flux',
        }
