from .json import JsonConfigHandler
from agent.logger import get_logger
from agent.pipeline.config_handlers import filtering_condition_parser

logger = get_logger(__name__)


class KafkaConfigHandler(JsonConfigHandler):
    def update_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + self.get_property_mapping(d) for d in self.client_config['dimensions']['required']]
                if self.client_config['value']['type'] == 'property':
                    conf['value'].append('/' + self.get_property_mapping(self.client_config['value']['value']))
                if self.client_config['timestamp']['name'] != 'kafka_timestamp':
                    conf['value'].append('/' + self.get_property_mapping(self.client_config['timestamp']['name']))
                if not self.client_config.get('static_what', True):
                    conf['value'].append('/' + self.get_property_mapping(self.client_config['measurement_name']))
                    conf['value'].append('/' + self.get_property_mapping(self.client_config['target_type']))
            if conf['name'] == 'stageRecordPreconditions':
                conf['value'] = []
                if not self.client_config.get('static_what', True):
                    expression = "record:value('/{0}') == 'gauge' || record:value('/{0}') == 'counter'"
                    conf['value'].append('${' + expression.format(self.get_property_mapping(self.client_config['target_type'])) + '}')
                if self.client_config.get('filter', {}).get('condition'):
                    conf['value'].append(filtering_condition_parser.get_filtering_expression(
                        self.client_config['filter']['condition']))

        super().update_properties(stage)

