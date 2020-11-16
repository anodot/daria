import requests

from agent.modules import proxy
from .base import BaseConfigHandler
from agent.modules.constants import HOSTNAME
from copy import deepcopy


class MonitoringConfigHandler(BaseConfigHandler):
    DECLARE_VARS_JS = """/*
state['host_id'] = 'host_id';
*/

state['host_id'] = '{host_id}';
state['host_name'] = '{host_name}';
state['previous'] = {{}};
state['streamsets_url'] = '{streamsets_url}'
"""

    def _override_stages(self):
        anodot_monitoring_stage = None
        for stage in self.config['stages']:
            if stage['instanceName'] == 'HTTPClient_03':
                for conf in stage['configuration']:
                    if conf['name'] in self.pipeline.destination.config:
                        conf['value'] = self.pipeline.destination.config[conf['name']]
                anodot_monitoring_stage = deepcopy(stage)
                anodot_monitoring_stage['instanceName'] = 'send_to_monitoring'

            if stage['instanceName'] == 'JavaScriptEvaluator_01':
                for conf in stage['configuration']:
                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            host_id=self.pipeline.destination.host_id,
                            host_name=HOSTNAME,
                            streamsets_url=self.pipeline.streamsets.url,
                        )

        # check if monitoring is available
        r = requests.post(self.pipeline.destination.monitoring_url,
                          proxies=proxy.get_config(self.pipeline.destination.proxy),
                          json=[],
                          timeout=5)
        if r.status_code == 200:
            for conf in anodot_monitoring_stage['configuration']:
                if conf['name'] == 'conf.resourceUrl':
                    conf['value'] = self.pipeline.destination.monitoring_url
            anodot_monitoring_stage['uiInfo']['yPos'] += 100
            anodot_monitoring_stage['uiInfo']['label'] = 'Anodot agents API'
            self.config['stages'].append(anodot_monitoring_stage)

    def _set_labels(self):
        pass
