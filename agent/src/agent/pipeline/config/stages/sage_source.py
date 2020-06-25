from .base import Stage
from agent.source.sage import SageSource


class Sage(Stage):
    def get_config(self) -> dict:
        return {'scriptConf.params': [
            {'key': 'SAGE_TOKEN', 'value': self.pipeline.source.config[SageSource.TOKEN]},
            {'key': 'SAGE_URL', 'value': self.pipeline.source.config[SageSource.URL]},
            {'key': 'QUERY', 'value': ''},
            {'key': 'INTERVAL', 'value': ''},
            {'key': 'DELAY', 'value': ''},
        ]}
