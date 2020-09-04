import json
import os

from agent.logger import get_logger
from agent.constants import ERRORS_DIR, AGENT_URL
from agent.constants import ROOT_DIR
from agent.pipeline import pipeline as p

logger = get_logger(__name__)


class BaseConfigHandler:
    """
    Overrides base config file
    """
    PIPELINE_BASE_CONFIG_NAME = ''
    BASE_PIPELINE_CONFIGS_PATH = os.path.join('pipeline', 'config', 'base_pipelines')

    stages = {}

    def __init__(self, pipeline: p.Pipeline):
        self.config = {}
        self.pipeline = pipeline

    def load_base_config(self):
        with open(os.path.join(ROOT_DIR, self.BASE_PIPELINE_CONFIGS_PATH, self.PIPELINE_BASE_CONFIG_NAME)) as f:
            data = json.load(f)

        return data['pipelineConfig']

    def set_labels(self):
        self.config['metadata']['labels'] = [self.pipeline.source.type,
                                             self.pipeline.destination.TYPE]

    def override_base_config(self, new_uuid=None, new_title=None):
        self.config = self.load_base_config()

        # create errors dir
        errors_dir = os.path.join(ERRORS_DIR, self.pipeline.name)
        if not os.path.isdir(errors_dir):
            os.makedirs(errors_dir)
            os.chmod(errors_dir, 0o777)
        if new_uuid:
            self.config['uuid'] = new_uuid
        if new_title:
            self.config['title'] = new_title

        self.override_pipeline_config()
        self.override_stages()
        self.set_labels()

        return self.config

    def override_stages(self):
        for stage in self.config['stages']:
            if stage['instanceName'] in self.stages:
                stage_config = self.stages[stage['instanceName']](self.pipeline, stage).get_config()
                for conf in stage['configuration']:
                    if conf['name'] in stage_config:
                        conf['value'] = stage_config[conf['name']]

    def get_pipeline_config(self) -> dict:
        return {
            'TOKEN': self.pipeline.destination.token,
            'PROTOCOL': self.pipeline.destination.PROTOCOL_20,
            'ANODOT_BASE_URL': self.pipeline.destination.url,
            'AGENT_URL': AGENT_URL,
        }

    def override_pipeline_config(self):
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [{'key': key, 'value': val} for key, val in self.get_pipeline_config().items()]

    def set_initial_offset(self):
        pass


class ConfigHandlerException(Exception):
    pass
