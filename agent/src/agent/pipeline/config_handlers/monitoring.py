import json
import os

from .base import BaseConfigHandler


class MonitoringConfigHandler(BaseConfigHandler):
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/Monitoring.json'

    DECLARE_VARS_JS = """/*
state['host_id'] = 'host_id';
*/

state['host_id'] = '{host_id}';
"""

    def load_base_config(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               self.PIPELINES_BASE_CONFIGS_PATH), 'r') as f:
            data = json.load(f)

        return data['pipelineConfig']

    def override_stages(self):

        for stage in self.config['stages']:
            if stage['instanceName'] == 'HTTPClient_03':
                for conf in stage['configuration']:
                    if conf['name'] in self.client_config['destination']['config']:
                        conf['value'] = self.client_config['destination']['config'][conf['name']]

            if stage['instanceName'] == 'JavaScriptEvaluator_01':
                for conf in stage['configuration']:
                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            host_id=self.client_config['destination']['host_id'])

    def set_labels(self):
        pass
