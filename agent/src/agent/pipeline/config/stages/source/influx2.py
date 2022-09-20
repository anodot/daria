import os

from base64 import b64encode
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
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
        ])
        return params

    def _get_url(self) -> str:
        api_endpoint = '/api/v2/query'
        if org_param := self.pipeline.source.config.get('org'):
            api_endpoint += f'?org={org_param}'
        return urljoin(self.pipeline.source.config['host'], api_endpoint)

    def _get_headers(self) -> dict:
        if self.pipeline.source.config.get('token'):
            auth_header = f'Token {self.pipeline.source.config.get("token")}'
        else:
            auth_key = f'{self.pipeline.source.config.get("username")}:{self.pipeline.source.config.get("password")}'
            auth_header = f'Basic {b64encode(auth_key.encode()).decode("ascii")}'
        return {
            'Authorization': auth_header,
            'Accept': 'application/csv',
            'Content-type': 'application/json',
        }

    def _get_query(self) -> str:
        query = self.pipeline.query or \
               f'from(bucket:"{self.pipeline.source.config["bucket"]}") ' \
               '|> {TIMESTAMP_CONDITION} ' \
               f'|> filter(fn: (r) => {self._get_filter_condition()}")'
        return query.replace(TIMESTAMP_CONDITION, 'range(start: %d, stop: %d)')

    def _get_filter_condition(self) -> str:
        filter_condition = f'r._measurement == "{self.pipeline.config["measurement_name"]}'
        custom_filtering = self.pipeline.config.get('filtering')
        if custom_filtering:
            filter_condition += f' and {custom_filtering}'
        return filter_condition


class TestInflux2Source(Influx2Source):
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
                'key': 'TIMEOUT',
                'value': self.pipeline.source.query_timeout
            },
            {
                'key': 'BUCKET',
                'value': self.pipeline.source.config.get('bucket', '')
            },
        ]

    def _get_url(self) -> str:
        return urljoin(self.pipeline.source.config['host'], '/api/v2/buckets')
