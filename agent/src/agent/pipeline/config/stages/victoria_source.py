import os
import pytz

from datetime import datetime
from agent.modules.constants import ROOT_DIR
from agent import source
from .base import Stage


class VictoriaScript(Stage):
    JYTHON_SCRIPT = 'victoria.py'

    def get_initial_timestamp(self) -> str:
        if self.pipeline.days_to_backfill:
            midnight = int(datetime.timestamp(
                datetime.now(pytz.timezone('UTC')).replace(hour=0, minute=0, second=0, microsecond=0)
            ))
            return str(midnight - int(self.pipeline.days_to_backfill) * 24 * 60 * 60)
        return ''

    def get_config(self) -> dict:
        with open(os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)) as f:
            return {
                'scriptConf.params': [
                    {'key': 'URL', 'value': self.pipeline.source.config[source.VictoriaMetricsSource.URL]},
                    {'key': 'USERNAME',
                     'value': self.pipeline.source.config.get(source.VictoriaMetricsSource.USERNAME, '')},
                    {'key': 'PASSWORD',
                     'value': self.pipeline.source.config.get(source.VictoriaMetricsSource.PASSWORD, '')},
                    {'key': 'QUERY', 'value': self.pipeline.config['query']},
                    {'key': 'INITIAL_TIMESTAMP', 'value': self.get_initial_timestamp()},
                    {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_MINUTES', 'value': str(self.pipeline.delay)},
                    {'key': 'VERIFY_SSL', 'value': '1' if self.pipeline.source.config.get('verify_ssl', True) else ''},
                    {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.config.get('query_timeout', 15))},
                    {'key': 'AGGREGATED_METRIC_NAME', 'value': str(self.pipeline.config.get('aggregated_metric_name'))},
                ],
                'script': f.read(),
            }
