from .json import JsonConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class KafkaConfigHandler(JsonConfigHandler):

    def update_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]
                if self.client_config['value']['type'] == 'property':
                    conf['value'].append('/' + self.client_config['value']['value'])
                if self.client_config['timestamp']['name'] != 'kafka_timestamp':
                    conf['value'].append('/' + self.client_config['timestamp']['name'])

            if conf['name'] == 'expressionProcessorConfigs':

                conf['value'][1]['expression'] = self.client_config['measurement_name']

                if 'target_type' in self.client_config:
                    conf['value'][2]['expression'] = self.client_config['target_type']

                if self.client_config['value']['type'] == 'property':
                    expression = f"record:value('/{self.client_config['value']['value']}')"
                    conf['value'][3]['expression'] = '${' + expression + '}'
                else:
                    conf['value'][3]['expression'] = self.client_config['value']['value']

                for key, val in self.client_config['properties'].items():
                    conf['value'].append({'fieldToSet': '/properties/' + key, 'expression': val})

