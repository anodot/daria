from .base import BaseConfigHandler
from agent.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)


class MongoConfigHandler(BaseConfigHandler):
    def update_expression_processor(self, conf):
        if self.client_config.get('static_what', True):
            conf['value'][1]['expression'] = self.client_config['measurement_name']
            conf['value'][2]['expression'] = self.client_config.get('target_type', 'gauge')
        else:
            expression = "record:value('/{}')"
            conf['value'][1]['expression'] = '${' + expression.format(
                self.get_property_mapping(self.client_config['measurement_name'])) + '}'
            conf['value'][2]['expression'] = '${' + expression.format(
                self.get_property_mapping(self.client_config['target_type'])) + '}'

        if self.client_config['value']['type'] == 'property':
            expression = f"record:value('/{self.get_property_mapping(self.client_config['value']['value'])}')"
            conf['value'][3]['expression'] = '${' + expression + '}'
        else:
            conf['value'][3]['expression'] = self.client_config['value']['value']

    def update_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'expressionProcessorConfigs':
                self.update_expression_processor(conf)
                break
        self.set_constant_properties(stage)

    def get_rename_mapping(self):
        rename_mapping = []
        timestamp = self.get_property_mapping(self.client_config['timestamp']['name'])

        if timestamp != 'timestamp':
            rename_mapping.append({'fromFieldExpression': '/' + timestamp,
                                   'toFieldExpression': '/timestamp'})

        for dim in self.get_dimensions():
            rename_mapping.append({
                'fromFieldExpression': '/' + self.get_property_mapping(dim),
                'toFieldExpression': '/properties/' + dim.replace('/', '_')
            })
        return rename_mapping

    def rename_fields_for_anodot_protocol(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'renameMapping':
                conf['value'] = self.get_rename_mapping()

            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + self.get_property_mapping(d) for d in
                                 self.client_config['dimensions']['required']]

    def override_stages(self):
        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] == 'ExpressionEvaluator_01':
                self.update_properties(stage)

            if stage['instanceName'] == 'FieldRenamer_01':
                self.rename_fields_for_anodot_protocol(stage)

            if stage['instanceName'] == 'ExpressionEvaluator_02':
                self.convert_timestamp_to_unix(stage)

        self.update_destination_config()

    def set_initial_offset(self):
        source_config = self.client_config['source']['config']

        initial_offset = str(source_config.get('configBean.initialOffset', '3'))
        if initial_offset.isdigit():
            timestamp = datetime.now() - timedelta(days=int(initial_offset))
            source_config['configBean.initialOffset'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def update_source_configs(self):
        if self.client_config['source']['config'].get('configBean.offsetType', 'OBJECTID') != 'STRING':
            self.set_initial_offset()
        super().update_source_configs()
