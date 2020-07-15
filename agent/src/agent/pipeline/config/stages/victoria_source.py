from agent import source
from .base import Stage


class VictoriaScript(Stage):
    def get_config(self) -> dict:
        return {'scriptConf.params': [
            {'key': 'VICTORIA_URL', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.URL]},
            {'key': 'VICTORIA_USERNAME', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.USERNAME]},
            {'key': 'VICTORIA_PASSWORD', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.PASSWORD]},
            {'key': 'QUERY', 'value': self.pipeline.config['query']},
            {'key': 'START', 'value': str(self.pipeline.config['start'])},
            {'key': 'END', 'value': str(self.pipeline.config['start'])},
        ]}
