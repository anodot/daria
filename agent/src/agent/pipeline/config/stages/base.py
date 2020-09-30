import os

from abc import ABC, abstractmethod
from agent.modules.constants import ROOT_DIR
from agent.pipeline import pipeline as p


class Stage(ABC):
    JYTHON_SCRIPT = ''
    JYTHON_SCRIPTS_PATH = os.path.join('pipeline', 'config', 'jython_scripts')

    def __init__(self, pipeline: p.Pipeline, sdc_stage: dict):
        self.pipeline = pipeline
        self.sdc_stage = sdc_stage
        self.config = self.get_config()

    @abstractmethod
    def get_config(self) -> dict:
        pass

    def update_sdc_stage(self):
        for conf in self.sdc_stage['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]

    def get_jython_file_path(self):
        return os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)
