from agent import source
from .base import Stage


class SageScript(Stage):
    def get_config(self) -> dict:
        with open(self.pipeline.query_file) as f:
            query = f.read()
        return {'scriptConf.params': [
            {'key': 'SAGE_TOKEN', 'value': self.pipeline.source.config[source.SageSource.TOKEN]},
            {'key': 'SAGE_URL', 'value': self.pipeline.source.config[source.SageSource.URL]},
            {'key': 'QUERY', 'value': query},
            {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
            {'key': 'DELAY', 'value': str(self.pipeline.delay)},
            {'key': 'DAYS_TO_BACKFILL', 'value': str(self.pipeline.days_to_backfill)},
        ]}
