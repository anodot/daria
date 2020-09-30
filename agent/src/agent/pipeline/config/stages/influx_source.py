from .base import Stage


class InfluxScript(Stage):
    JYTHON_SCRIPT = 'influx.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'INITIAL_OFFSET', 'value': self.pipeline.source.config.get('offset', '')},
                    {'key': 'INTERVAL_IN_MINUTES', 'value': str(self.pipeline.config.get('interval', ''))},
                ],
                'script': f.read(),
            }
