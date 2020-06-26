from .base import Stage
from agent.source.sage import SageSource


class Sage(Stage):
    def get_config(self) -> dict:
        with open(self.pipeline.query_file) as f:
            query = f.read()
        return {'scriptConf.params': [
            {'key': 'SAGE_TOKEN', 'value': self.pipeline.source.config[SageSource.TOKEN]},
            {'key': 'SAGE_URL', 'value': self.pipeline.source.config[SageSource.URL]},
            {'key': 'QUERY', 'value': query},
            {'key': 'INTERVAL', 'value': self.pipeline.interval},
            {'key': 'DELAY', 'value': self.pipeline.delay},
        ]}
