import os

from agent.constants import ROOT_DIR
from agent import source
from .base import Stage


class VictoriaScript(Stage):
    JYTHON_SCRIPT = 'victoria.py'

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
                    {'key': 'DAYS_TO_BACKFILL', 'value': str(self.pipeline.days_to_backfill)},
                    {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_MINUTES', 'value': str(self.pipeline.delay)},
                ],
                'script': f.read(),
            }
