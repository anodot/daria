import os
import pytz

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline


class Stage(ABC):
    JYTHON_SCRIPT = ''
    JYTHON_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'jython_scripts')
    JS_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'js_scripts')

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_

    @abstractmethod
    def get_config(self) -> dict:
        pass

    def get_jython_file_path(self):
        return os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)

    def _get_js_file_path(self, name: str):
        return os.path.join(ROOT_DIR, self.JS_SCRIPTS_PATH, name)

    def get_initial_timestamp(self) -> datetime:
        midnight = datetime.now(pytz.timezone('UTC')).replace(hour=0, minute=0, second=0, microsecond=0)
        return midnight - timedelta(days=int(self.pipeline.days_to_backfill))
