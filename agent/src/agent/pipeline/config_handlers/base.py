import json
import os

from abc import ABC, abstractmethod
from agent.logger import get_logger
from agent.constants import ERRORS_DIR
from copy import deepcopy

logger = get_logger(__name__)


class BaseConfigHandler(ABC):
    """
    Overrides base config file
    """
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/{source_name}_{destination_name}.json'

    def __init__(self, client_config, base_config=None):
        self.client_config = deepcopy(client_config)

        self.config = base_config if base_config else self.load_base_config()

        # create errors dir
        errors_dir = os.path.join(ERRORS_DIR, self.client_config['pipeline_id'])
        if not os.path.isdir(errors_dir):
            os.makedirs(errors_dir)
            os.chmod(errors_dir, 0o777)

    def load_base_config(self):
        base_path = self.PIPELINES_BASE_CONFIGS_PATH.format(**{
            'source_name': self.client_config['source']['type'],
            'destination_name': self.client_config['destination']['type']
        })
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), base_path), 'r') as f:
            data = json.load(f)

        return data['pipelineConfig']

    @abstractmethod
    def override_stages(self):
        ...

    def set_labels(self):
        self.config['metadata']['labels'] = [self.client_config['source']['type'],
                                             self.client_config['destination']['type']]

    def override_base_config(self, new_uuid=None, new_pipeline_title=None):
        if new_uuid:
            self.config['uuid'] = new_uuid
        if new_pipeline_title:
            self.config['title'] = new_pipeline_title

        self.override_stages()
        self.set_labels()

        return self.config

    def update_source_configs(self):
        for conf in self.config['stages'][0]['configuration']:
            if conf['name'] in self.client_config['source']['config']:
                conf['value'] = self.client_config['source']['config'][conf['name']]

    def get_dimensions(self):
        dimensions = self.client_config['dimensions']['required']
        if 'optional' in self.client_config['dimensions']:
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
        return dimensions

    def update_destination_config(self):
        for conf in self.config['stages'][-1]['configuration']:
            if conf['name'] in self.client_config['destination']['config']:
                conf['value'] = self.client_config['destination']['config'][conf['name']]


class ConfigHandlerException(Exception):
    pass
