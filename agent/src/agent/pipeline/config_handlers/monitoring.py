import json
import os

from .base import BaseConfigHandler


class MonitoringConfigHandler(BaseConfigHandler):
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/Monitoring.json'

    def load_base_config(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               self.PIPELINES_BASE_CONFIGS_PATH), 'r') as f:
            data = json.load(f)

        return data['pipelineConfig']

    def override_stages(self):
        self.update_destination_config()

    def set_labels(self):
        pass
