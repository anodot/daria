from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config import schema
from agent.pipeline.config.stages import JSConvertMetrics

logger = get_logger(__name__)


class JDBCProtocol30SDCConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'directory_httpv3.json'

    stages = {'JavaScriptEvaluator_01': JSConvertMetrics}

    def override_stages(self):
        self.update_pipeline_config()
        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] in self.stages:
                stage_config = self.stages[stage['instanceName']](self.pipeline, stage).get_config()
                for conf in stage['configuration']:
                    if conf['name'] in stage_config:
                        conf['value'] = stage_config[conf['name']]

        self.update_destination_config()

    def update_pipeline_config(self):
        schema_definition = schema.update(self.pipeline)
        self.pipeline.config.update(schema_definition)
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [
                    {'key': 'SCHEMA_ID', 'value': self.pipeline.get_schema_id()},
                    {'key': 'TOKEN', 'value': self.pipeline.destination.token},
                    {'key': 'PROTOCOL', 'value': self.pipeline.destination.PROTOCOL_30},
                    {'key': 'ANODOT_BASE_URL', 'value': self.pipeline.destination.url},
                ]

    def update_destination_config(self):
        for stage in self.config['stages']:
            if stage['instanceName'] in ['destination', 'destination_watermark']:
                for conf in stage['configuration']:
                    if conf['name'] in self.pipeline.destination.config and conf['name'] != self.pipeline.destination.CONFIG_RESOURCE_URL:
                        conf['value'] = self.pipeline.destination.config[conf['name']]

    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/dimensions/' + key
