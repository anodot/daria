from .base import BaseConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class JsonConfigHandler(BaseConfigHandler):

    def update_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            conf['value'][1]['expression'] = self.client_config['measurement_name']

            if 'target_type' in self.client_config:
                conf['value'][2]['expression'] = self.client_config['target_type']

            if self.client_config['value']['type'] == 'column':
                expression = f"record:value('/{self.client_config['value']['value']}')"
                conf['value'][3]['expression'] = '${' + expression + '}'
            else:
                conf['value'][3]['expression'] = self.client_config['value']['value']

            return

    def get_rename_mapping(self):
        rename_mapping = []

        if self.client_config['timestamp']['name'] != 'timestamp':
            rename_mapping.append({'fromFieldExpression': '/' + self.client_config['timestamp']['name'],
                                   'toFieldExpression': '/timestamp'})

        for dim in self.get_dimensions():
            rename_mapping.append({
                'fromFieldExpression': '/' + dim,
                'toFieldExpression': '/properties/' + dim.replace('/', '_')
            })
        return rename_mapping

    def rename_fields_for_anodot_protocol(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'renameMapping':
                conf['value'] = self.get_rename_mapping()

            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]

    def convert_timestamp_to_unix(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            if self.client_config['timestamp']['type'] == 'string':
                dt_format = self.client_config['timestamp']['format']
                get_timestamp_exp = f"time:extractDateFromString(record:value('/timestamp'), '{dt_format}')"
                expression = f"time:dateTimeToMilliseconds({get_timestamp_exp})/1000"
            elif self.client_config['timestamp']['type'] == 'datetime':
                expression = "time:dateTimeToMilliseconds(record:value('/timestamp'))/1000"
            elif self.client_config['timestamp']['type'] == 'unix_ms':
                expression = "record:value('/timestamp')/1000"
            else:
                expression = "record:value('/timestamp')"

            conf['value'][0]['expression'] = '${' + expression + '}'
            return

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
