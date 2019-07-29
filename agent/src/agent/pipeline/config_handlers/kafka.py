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
                if not self.client_config.get('static_what', True):
                    conf['value'].append('/' + self.client_config['measurement_name'])
                    conf['value'].append('/' + self.client_config['target_type'])
            if conf['name'] == 'stageRecordPreconditions' and not self.client_config.get('static_what', True):
                expression = "record:value('/{0}') == 'gauge' || record:value('/{0}') == 'counter'"
                conf['value'].append('${' + expression.format(self.client_config['target_type']) + '}')

            if conf['name'] == 'expressionProcessorConfigs':

                self.update_expression_processor(conf)

