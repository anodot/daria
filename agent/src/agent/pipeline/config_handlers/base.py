import json
import os

from abc import ABC, abstractmethod
from agent.logger import get_logger
from agent.constants import ERRORS_DIR, HOSTNAME
from agent.pipeline.pipeline import Pipeline
from copy import deepcopy

logger = get_logger(__name__)


class BaseConfigHandler(ABC):
    """
    Overrides base config file
    """
    PIPELINE_BASE_CONFIG_NAME = ''

    def __init__(self, pipeline: Pipeline):
        self.client_config = {}
        self.config = {}
        self.pipeline = pipeline

    def get_pipeline_type(self) -> str:
        return self.pipeline.source.type

    def load_base_config(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'base_pipelines',
                               self.PIPELINE_BASE_CONFIG_NAME), 'r') as f:
            data = json.load(f)

        return data['pipelineConfig']

    @abstractmethod
    def override_stages(self):
        ...

    def set_labels(self):
        self.config['metadata']['labels'] = [self.pipeline.source.type,
                                             self.client_config['destination']['type']]

    def override_base_config(self, client_config, new_uuid=None, new_pipeline_title=None, base_config=None):
        self.client_config = deepcopy(client_config)

        self.config = base_config if base_config else self.load_base_config()

        # create errors dir
        errors_dir = os.path.join(ERRORS_DIR, self.client_config['pipeline_id'])
        if not os.path.isdir(errors_dir):
            os.makedirs(errors_dir)
            os.chmod(errors_dir, 0o777)
        if new_uuid:
            self.config['uuid'] = new_uuid
        if new_pipeline_title:
            self.config['title'] = new_pipeline_title

        self.override_stages()
        self.set_labels()

        return self.config

    def update_source_configs(self):
        if 'library' in self.pipeline.source.config:
            self.config['stages'][0]['library'] = self.pipeline.source.config['library']
        for conf in self.config['stages'][0]['configuration']:
            if conf['name'] in self.pipeline.source.config:
                conf['value'] = self.pipeline.source.config[conf['name']]

    def get_dimensions(self):
        dimensions = self.client_config['dimensions']['required']
        if 'optional' in self.client_config['dimensions']:
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
        return dimensions

    def update_destination_config(self):
        for stage in self.config['stages']:
            if stage['instanceName'] == 'destination':
                for conf in stage['configuration']:
                    if conf['name'] in self.pipeline.destination.config:
                        conf['value'] = self.pipeline.destination.config[conf['name']]

    def get_convert_timestamp_to_unix_expression(self, value):
        if self.client_config['timestamp']['type'] == 'string':
            dt_format = self.client_config['timestamp']['format']
            return f"time:dateTimeToMilliseconds(time:extractDateFromString({value}, '{dt_format}'))/1000"
        elif self.client_config['timestamp']['type'] == 'datetime':
            return f"time:dateTimeToMilliseconds({value})/1000"
        elif self.client_config['timestamp']['type'] == 'unix_ms':
            return f"{value}/1000"
        return value

    def convert_timestamp_to_unix(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue
            value = "record:value('/timestamp')"
            conf['value'][0]['expression'] = '${' + self.get_convert_timestamp_to_unix_expression(value) + '}'
            return

    def get_default_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.client_config['destination']['host_id']],
            'source_host_name': [HOSTNAME],
            'pipeline_id': [self.pipeline.id],
            'pipeline_type': [self.get_pipeline_type()]
        }

    def get_tags(self) -> dict:
        return {
            **self.get_default_tags(),
            **self.client_config.get('tags', {})
        }

    def set_constant_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            for key, val in self.client_config.get('properties', {}).items():
                conf['value'].append({'fieldToSet': '/properties/' + key, 'expression': val})

            conf['value'].append({'fieldToSet': '/tags', 'expression': '${emptyMap()}'})
            for tag_name, tag_values in self.get_tags().items():
                conf['value'].append({'fieldToSet': f'/tags/{tag_name}', 'expression': '${emptyList()}'})
                for idx, val in enumerate(tag_values):
                    conf['value'].append({'fieldToSet': f'/tags/{tag_name}[{idx}]', 'expression': val})
            return

    def set_initial_offset(self, client_config=None):
        pass

    def get_property_mapping(self, property_value):
        mapping = self.pipeline.source.config.get('csv_mapping', {})
        for idx, item in mapping.items():
            if item == property_value:
                return idx

        return property_value


class ConfigHandlerException(Exception):
    pass
