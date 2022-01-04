import os
import urllib.parse

from urllib.parse import urljoin
from agent.pipeline.config.stages.influx import InfluxScript
from agent.pipeline.config.stages.base import JythonSource


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
                'value': urllib.parse.urljoin(
                    self.pipeline.streamsets.agent_external_url, f'/monitoring/source_http_error/{self.pipeline.name}/'
                )
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
        return f'from(bucket:"{self.pipeline.source.config["bucket"]}") ' \
               '|> range(start: {}, stop: {}) ' \
               f'|> filter(fn: (r) => {self._get_filter_condition()}")'

    def _get_filter_condition(self) -> str:
        filter_condition = f'r._measurement == "{self.pipeline.config["measurement_name"]}'
        custom_filtering = self.pipeline.config.get('filtering')
        if custom_filtering:
            filter_condition += f' and {custom_filtering}'
        return filter_condition


class TestInflux2Source(JythonSource):
    JYTHON_SCRIPT = 'influx2.py'
    JYTHON_SCRIPTS_PATH = os.path.join(JythonSource.JYTHON_SCRIPTS_PATH, 'test_pipelines')

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
        ]

    def _get_url(self) -> str:
        return urljoin(self.pipeline.source.config['host'], '/api/v2/buckets')

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Token {self.pipeline.source.config["token"]}',
            'Accept': 'application/csv',
            'Content-type': 'application/vnd.flux',
        }
