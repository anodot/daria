from agent import source
from .base import Stage


class VictoriaScript(Stage):
    def get_config(self) -> dict:
        return {'scriptConf.params': [
            # todo
            {'key': 'VICTORIA_URL', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.URL]},
            # {'key': 'VICTORIA_USERNAME', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.USERNAME]},
            # {'key': 'VICTORIA_PASSWORD', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.PASSWORD]},
            {'key': 'QUERY', 'value': self.pipeline.config['query']},
            {'key': 'DAYS_TO_BACKFILL', 'value': str(self.pipeline.days_to_backfill)},
            {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
        ]}
