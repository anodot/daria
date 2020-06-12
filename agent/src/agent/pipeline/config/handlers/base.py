import json
import os

from agent.logger import get_logger
from agent.constants import ERRORS_DIR
from agent.pipeline.pipeline import Pipeline
from copy import deepcopy
from agent.definitions import ROOT_DIR

logger = get_logger(__name__)


class BaseConfigHandler():
    """
    Overrides base config file
    """
    PIPELINE_BASE_CONFIG_NAME = ''
    BASE_PIPELINE_CONFIGS_PATH = os.path.join('pipeline', 'config', 'base_pipelines')

    stages = {}

    def __init__(self, pipeline: Pipeline):
        self.client_config = {}
        self.config = {}
        self.pipeline = pipeline

    def get_pipeline_type(self) -> str:
        return self.pipeline.source.type

    def load_base_config(self):
        with open(os.path.join(ROOT_DIR, self.BASE_PIPELINE_CONFIGS_PATH, self.PIPELINE_BASE_CONFIG_NAME)) as f:
            data = json.load(f)

        return data['pipelineConfig']

    def set_labels(self):
        self.config['metadata']['labels'] = [self.pipeline.source.type,
                                             self.pipeline.destination.TYPE]

    def override_base_config(self, client_config, new_uuid=None, new_pipeline_title=None, base_config=None):
        self.client_config = deepcopy(client_config)

        self.config = base_config if base_config else self.load_base_config()

        # create errors dir
        errors_dir = os.path.join(ERRORS_DIR, self.client_config['pipeline_id'])
        if not os.path.isdir(errors_dir):
            os.makedirs(errors_dir)
            os.chmod(errors_dir, 0o777)
        if new_uuid:
            self.config['uuid'] = new_uuid
        if new_pipeline_title:
            self.config['title'] = new_pipeline_title

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


class ConfigHandlerException(Exception):
    pass
