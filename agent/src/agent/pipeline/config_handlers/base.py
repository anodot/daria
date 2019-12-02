import json
import os

from abc import ABC, abstractmethod
from agent.logger import get_logger
from agent.constants import ERRORS_DIR, HOSTNAME
from copy import deepcopy

logger = get_logger(__name__)


class BaseConfigHandler(ABC):
    """
    Overrides base config file
    """
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/{source_name}_{destination_name}.json'

    def __init__(self):
        self.client_config = {}
        self.config = {}

    def get_pipeline_id(self):
        return self.client_config['pipeline_id']

    def load_base_config(self):
        base_path = self.PIPELINES_BASE_CONFIGS_PATH.format(**{
            'source_name': self.client_config['source']['type'],
            'destination_name': self.client_config['destination']['type']
        })
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), base_path), 'r') as f:
            data = json.load(f)

        return data['pipelineConfig']

    @abstractmethod
    def override_stages(self):
        ...

    def set_labels(self):
        self.config['metadata']['labels'] = [self.client_config['source']['type'],
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
        if 'library' in self.client_config['source']['config']:
            self.config['stages'][0]['library'] = self.client_config['source']['config']['library']
        for conf in self.config['stages'][0]['configuration']:
            if conf['name'] in self.client_config['source']['config']:
                conf['value'] = self.client_config['source']['config'][conf['name']]

    def get_dimensions(self):
        dimensions = self.client_config['dimensions']['required']
        if 'optional' in self.client_config['dimensions']:
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
        return dimensions

    def update_destination_config(self):
        for stage in self.config['stages']:
            if stage['instanceName'] == 'destination':
                for conf in stage['configuration']:
                    if conf['name'] in self.client_config['destination']['config']:
                        conf['value'] = self.client_config['destination']['config'][conf['name']]

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

    def set_constant_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            for key, val in self.client_config.get('properties', {}).items():
                conf['value'].append({'fieldToSet': '/properties/' + key, 'expression': val})

            conf['value'].append({'fieldToSet': '/tags', 'expression': '${emptyMap()}'})
            conf['value'].append({'fieldToSet': '/tags/source', 'expression': '${emptyList()}'})
            conf['value'].append({'fieldToSet': '/tags/source_host_id', 'expression': '${emptyList()}'})
            conf['value'].append({'fieldToSet': '/tags/source_host_name', 'expression': '${emptyList()}'})
            conf['value'].append({'fieldToSet': '/tags/pipeline_id', 'expression': '${emptyList()}'})
            conf['value'].append({'fieldToSet': '/tags/source[0]', 'expression': 'anodot-agent'})
            conf['value'].append({'fieldToSet': '/tags/source_host_id[0]',
                                  'expression': self.client_config['destination']['host_id']})
            conf['value'].append({'fieldToSet': '/tags/source_host_name[0]',
                                  'expression': HOSTNAME})
            conf['value'].append({'fieldToSet': '/tags/pipeline_id[0]', 'expression': self.get_pipeline_id()})
            return

    def set_initial_offset(self, client_config=None):
        pass

    def get_property_mapping(self, property_value):
        mapping = self.client_config['source']['config'].get('csv_mapping', {})
        for idx, item in mapping.items():
            if item == property_value:
                return idx

        return property_value


class ConfigHandlerException(Exception):
    pass
