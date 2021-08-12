from urllib.parse import urljoin
from agent.pipeline.config.stages.influx import InfluxScript


class Influx2Source(InfluxScript):
    JYTHON_SCRIPT = 'influx2.py'

    def get_config(self) -> dict:
        config = super().get_config()
        config['scriptConf.params'].extend([
            {'key': 'URL', 'value': self._get_url()},
            {'key': 'HEADERS', 'value': self._get_headers()},
            {'key': 'DATA', 'value': self._get_data()},
        ])
        return config

    def _get_url(self) -> str:
        return urljoin(self.pipeline.source.config['host'], f'/api/v2/query?org={self.pipeline.source.config["org"]}')

    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Token {self.pipeline.source.config["token"]}',
            'Accept': 'application/csv',
            'Content-type': 'application/vnd.flux',
        }

    def _get_data(self) -> str:
        return f'from(bucket:"{self.pipeline.source.config["bucket"]}") ' \
               '|> range(start: {}, stop: {}) ' \
               f'|> filter(fn: (r) => r._measurement == "{self.pipeline.config["measurement_name"]}")'
