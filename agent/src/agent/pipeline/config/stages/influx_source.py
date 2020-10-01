from .base import Stage


class InfluxScript(Stage):
    JYTHON_SCRIPT = 'influx.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'INITIAL_OFFSET', 'value': self.pipeline.source.config.get('offset', '')},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.config.get('interval', ''))},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(convert_to_seconds(self.pipeline.config.get('delay', '0s')))},
                ],
                'script': f.read(),
            }


def convert_to_seconds(string):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(string[:-1]) * seconds_per_unit[string[-1]]
