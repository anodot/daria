import os
import urllib.parse
import pytz

from functools import reduce
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


class JSScript(Stage, ABC):
    JS_SCRIPT_NAME = ''
    JS_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'js_scripts')

    def _get_script(self) -> str:
        with open(os.path.join(ROOT_DIR, self.JS_SCRIPTS_PATH, self.JS_SCRIPT_NAME)) as f:
            return f.read()


class JythonScript(Stage, ABC):
    PARAMS_KEY = ''
    JYTHON_SCRIPT = ''
    JYTHON_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'jython_scripts')

    @abstractmethod
    def _get_script_params(self) -> list[dict]:
        pass

    def get_config(self) -> dict:
        return {self.PARAMS_KEY: self._get_script_params(), 'script': self._get_script()}

    def _get_script(self) -> str:
        with open(self._get_jython_file_path()) as f:
            return f.read().replace("'%TRANSFORM_SCRIPT_PLACEHOLDER%'", self.pipeline.transform_script_config or '')

    def _get_jython_file_path(self):
        return os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)


class JythonSource(JythonScript, ABC):
    PARAMS_KEY = 'scriptConf.params'


class JythonProcessor(JythonScript, ABC):
    PARAMS_KEY = 'userParams'


class JythonDataExtractorSource(JythonSource, ABC):
    DATA_EXTRACTOR_API_ENDPOINT = ''

    def _get_source_url(self) -> str:
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url, '/'.join([
                'data_extractors',
                self.DATA_EXTRACTOR_API_ENDPOINT,
                '${pipeline:id()}',
            ])
        )
