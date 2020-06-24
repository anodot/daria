from .base import Stage


class SageSource(Stage):
    def get_config(self) -> dict:
        return {'scriptConf.params': [
            {'key': 'SAGE_TOKEN', 'value': ''},
            {'key': 'SAGE_URL', 'value': ''},
            {'key': 'QUERY', 'value': ''},
            {'key': 'INTERVAL', 'value': ''},
            {'key': 'DELAY', 'value': ''},
        ]}
