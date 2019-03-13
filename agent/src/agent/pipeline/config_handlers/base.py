import json
import os

from abc import ABC, abstractmethod
from agent.logger import get_logger

logger = get_logger(__name__)


class BaseConfigHandler(ABC):
    """
    Overrides base config file
    """
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/{source_name}_{destination_name}.json'

    def __init__(self, client_config, base_config=None):
        self.client_config = client_config

        if base_config:
            self.config = base_config
        else:
            base_path = self.PIPELINES_BASE_CONFIGS_PATH.format(**{
                'source_name': client_config['source']['type'],
                'destination_name': client_config['destination']['type']
            })
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), base_path), 'r') as f:
                data = json.load(f)
                self.config = data['pipelineConfig']
                self.rules = data['pipelineRules']

    @abstractmethod
    def override_base_config(self, new_uuid=None, new_pipeline_title=None):
        ...

    @abstractmethod
    def override_base_rules(self, new_uuid):
        ...
