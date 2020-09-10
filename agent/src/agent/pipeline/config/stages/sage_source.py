import os

from agent import source
from agent.constants import ROOT_DIR
from .base import Stage


class SageScript(Stage):
    JYTHON_SCRIPT = 'sage.py'

    def get_config(self) -> dict:
        with open(self.pipeline.query_file) as f:
            query = f.read()
        with open(os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)) as f:
            script = f.read()

        return {
            'scriptConf.params': [
                {'key': 'PIPELINE_NAME', 'value': self.pipeline.name},
                {'key': 'SAGE_TOKEN', 'value': self.pipeline.source.config[source.SageSource.TOKEN]},
                {'key': 'SAGE_URL', 'value': self.pipeline.source.config[source.SageSource.URL]},
                {'key': 'QUERY', 'value': query},
                {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
                {'key': 'DELAY', 'value': str(self.pipeline.delay)},
                {'key': 'DAYS_TO_BACKFILL', 'value': str(self.pipeline.days_to_backfill)},
                {'key': 'QUERY_SIZE', 'value': str(self.pipeline.batch_size)},
            ],
            'script': script
        }
