from .base import Stage


class JDBCScript(Stage):
    JYTHON_SCRIPT = 'jdbc.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'INITIAL_OFFSET', 'value': self.get_initial_timestamp().strftime('%d/%m/%Y %H:%M')},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                ],
                'script': f.read(),
            }
