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

                self.update_expression_processor(conf)

