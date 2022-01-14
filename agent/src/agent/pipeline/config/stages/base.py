import os
import urllib.parse
import pytz

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline


class Stage(ABC):
    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_

    @abstractmethod
    def get_config(self) -> dict:
        pass

    def get_initial_timestamp(self) -> datetime:
        midnight = datetime.now(pytz.timezone('UTC')).replace(hour=0, minute=0, second=0, microsecond=0)
        return midnight - timedelta(days=int(self.pipeline.days_to_backfill))


class JSProcessor(Stage, ABC):
    JS_SCRIPT_NAME = ''
    JS_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'js_scripts')

    def _get_script(self) -> str:
        with open(os.path.join(ROOT_DIR, self.JS_SCRIPTS_PATH, self.JS_SCRIPT_NAME)) as f:
            return f.read()


class _JythonScript(Stage, ABC):
    PARAMS_KEY = ''
    JYTHON_SCRIPT = ''
    JYTHON_SCRIPTS_DIR = os.path.join('pipeline', 'config', 'jython_scripts')

    @abstractmethod
    def _get_script_params(self) -> list[dict]:
        pass

    def get_config(self) -> dict:
        return {self.PARAMS_KEY: self._get_script_params(), 'script': self._get_script()}

    def _get_script(self) -> str:
        with open(os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_DIR, self.JYTHON_SCRIPT)) as f:
            return f.read().replace("'%TRANSFORM_SCRIPT_PLACEHOLDER%'", self.pipeline.transform_script_config or '')


class JythonSource(_JythonScript, ABC):
    PARAMS_KEY = 'scriptConf.params'


class JythonProcessor(_JythonScript, ABC):
    PARAMS_KEY = 'userParams'


class JythonDataExtractorSource(JythonSource, ABC):
    DATA_EXTRACTOR_API_ENDPOINT = ''

    def _get_source_url(self) -> str:
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url, '/'.join([
                self.DATA_EXTRACTOR_API_ENDPOINT,
                '${pipeline:id()}',
            ])
        )
