from .base import Stage
from datetime import datetime, timedelta


class JDBCScript(Stage):
    JYTHON_SCRIPT = 'jdbc.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'INITIAL_OFFSET', 'value': self._get_initial_offset()},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                ],
                'script': f.read(),
            }

    def _get_initial_offset(self) -> str:
        return (datetime.now() - timedelta(days=int(self.pipeline.days_to_backfill))).strftime('%d/%m/%Y %H:%M')
