import json
import os

from .logger import get_logger

logger = get_logger(__name__)


class PipelineConfigHandler:
    """
    Overrides base config file
    """
    PIPELINES_BASE_CONFIGS_PATH = 'pipelines/{source_name}.json'

    def __init__(self, client_config):
        self.client_config = client_config

        base_path = self.PIPELINES_BASE_CONFIGS_PATH.format(**{'source_name': client_config['source_name']})
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), base_path), 'r') as f:
            data = json.load(f)
            self.config = data['pipelineConfig']
            self.rules = data['pipelineRules']

    def update_source_configs(self):
        for conf in self.config['stages'][0]['configuration']:
            if conf['name'] in self.client_config['source_config']:
                conf['value'] = self.client_config['source_config'][conf['name']]

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

        dimensions = self.client_config['dimensions']['required']
        if 'optional' in self.client_config['dimensions']:
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
        for dim in dimensions:
            rename_mapping.append({'fromFieldExpression': '/' + dim, 'toFieldExpression': '/properties/' + dim})
        return rename_mapping

    def rename_fields_for_anodot_protocol(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'renameMapping':
                conf['value'] = self.get_rename_mapping()

            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]

    def update_http_client(self):
        for conf in self.config['stages'][len(self.config['stages']) - 1]['configuration']:
            if conf['name'] == 'conf.resourceUrl':
                conf['value'] = self.client_config['destination_url']

    def convert_timestamp_to_unix(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            if self.client_config['timestamp']['type'] == 'string':
                expression = f"time:dateTimeToMilliseconds(time:extractDateFromString(record:value('/timestamp'), '{self.client_config['timestamp']['format']}'))/1000"
            elif self.client_config['timestamp']['type'] == 'datetime':
                expression = "time:dateTimeToMilliseconds(record:value('/timestamp'))/1000"
            elif self.client_config['timestamp']['type'] == 'unix_ms':
                expression = "record:value('/timestamp')/1000"
            else:
                expression = "record:value('/timestamp')"

            conf['value'][0]['expression'] = '${' + expression + '}'
            return

    def override_base_config(self, new_uuid, new_pipeline_title):
        self.config['uuid'] = new_uuid
        self.config['title'] = new_pipeline_title

        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] == 'ExpressionEvaluator_01':
                self.update_properties(stage)

            if stage['instanceName'] == 'FieldRenamer_01':
                self.rename_fields_for_anodot_protocol(stage)

            if stage['instanceName'] == 'ExpressionEvaluator_02':
                self.convert_timestamp_to_unix(stage)

        self.update_http_client()

        return self.config

    def override_base_rules(self, new_uuid):
        self.rules['uuid'] = new_uuid
        return self.rules
