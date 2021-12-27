import os
import urllib.parse
import pytz

from functools import reduce
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

    # todo remove unneeded code from all stages that overwrite get_config after review
    @abstractmethod
    def get_config(self) -> dict:
        pass

    # todo it should be only in jython
    def get_jython_file_path(self):
        return os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)

    # todo it should be only in js
    def _get_js_file_path(self, name: str):
        return os.path.join(ROOT_DIR, self.JS_SCRIPTS_PATH, name)

    def get_initial_timestamp(self) -> datetime:
        midnight = datetime.now(pytz.timezone('UTC')).replace(hour=0, minute=0, second=0, microsecond=0)
        return midnight - timedelta(days=int(self.pipeline.days_to_backfill))


class JythonScript(Stage, ABC):
    def _get_script(self) -> str:
        # todo it might be the same for jython and js scripts
        with open(self.get_jython_file_path()) as f:
            return f.read()

    def _get_script_params(self) -> list[dict]:
        # todo it should be abstract
        return []


class JythonSource(JythonScript, ABC):
    def get_config(self) -> dict:
        return {'scriptConf.params': self._get_script_params(), 'script': self._get_script()}


class JythonDataExtractorSource(JythonSource, ABC):
    DATA_EXTRACTOR_API_PATH = ''

    def _get_source_url(self) -> str:
        return reduce(
            urllib.parse.urljoin,
            [self.pipeline.streamsets.agent_external_url, self.DATA_EXTRACTOR_API_PATH, '${pipeline:id()}']
        )


class JythonProcessor(JythonScript, ABC):
    def get_config(self) -> dict:
        return {'userParams': self._get_script_params(), 'script': self._get_script()}
