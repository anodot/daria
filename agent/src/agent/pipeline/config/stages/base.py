import os

from abc import ABC, abstractmethod
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline
from agent import pipeline


class Stage(ABC):
    JYTHON_SCRIPT = ''
    JYTHON_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'jython_scripts')

    def __init__(self, pipeline_: Pipeline, sdc_stage: dict):
        self.pipeline = pipeline_
        self.sdc_stage = sdc_stage
        if isinstance(pipeline_, pipeline.TestPipeline):
            self.config = self._get_source_config()
        else:
            self.config = self._get_config()

    def _get_source_config(self):
        return {**self.pipeline.source.config, **self.pipeline.override_source}

    @abstractmethod
    def _get_config(self) -> dict:
        pass

    def get_jython_file_path(self):
        return os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)
