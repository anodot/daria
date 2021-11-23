import urllib.parse

from agent import source
from agent.pipeline.config.stages.source import Source


class ObserviumScript(Source):
    JYTHON_SCRIPT = 'observium.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            script = f.read()
        base_url = urllib.parse.urljoin(
            self.pipeline.source.config[source.ObserviumSource.URL],
            '/api/v0/'
        )
        return {
            'scriptConf.params': [
                {'key': 'ENDPOINT', 'value': self.pipeline.source.config['endpoint']},
                {'key': 'DEVICES_URL', 'value': urllib.parse.urljoin(base_url, 'devices')},
                {'key': 'URL', 'value': urllib.parse.urljoin(base_url, self.pipeline.source.config['endpoint'])},
                {'key': 'API_USER', 'value': self.pipeline.source.config[source.ObserviumSource.USERNAME]},
                {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.ObserviumSource.PASSWORD]},
                {'key': 'REQUEST_PARAMS', 'value': self.pipeline.config.get('request_params', {})},
                {'key': 'MEASUREMENTS', 'value': list(self.pipeline.value_paths)},
                {'key': 'DIMENSIONS', 'value': self.pipeline.dimension_paths_with_names},
                {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.query_timeout)},
                {'key': 'VERIFY_SSL', 'value': '1' if self.pipeline.source.config.get('verify_ssl', True) else ''},
                {'key': 'SCHEMA_ID', 'value': self.pipeline.get_schema_id()},
                {'key': 'MONITORING_URL', 'value': self._monitoring_url()},
            ],
            'script': script
        }

    def _monitoring_url(self):
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url,
            f'/monitoring/source_http_error/{self.pipeline.name}/'
        )
