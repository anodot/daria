import json
import os
import time

from abc import ABC, abstractmethod
from agent.constants import DATA_DIR
from agent.tools import if_validation_enabled, sdc_record_map_to_dict
from jsonschema import validate, ValidationError
from agent.streamsets_api_client import api_client, StreamSetsApiClientException


class Source(ABC):
    VALIDATION_SCHEMA_FILE_NAME = ''
    TEST_PIPELINE_NAME = ''
    DIR = os.path.join(DATA_DIR, 'sources')
    MAX_SAMPLE_RECORDS = 3

    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    @classmethod
    def get_file_path(cls, name: str) -> str:
        return os.path.join(cls.DIR, name + '.json')

    @classmethod
    def exists(cls, name: str) -> bool:
        return os.path.isfile(cls.get_file_path(name))

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.name)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def create(self):
        if self.exists(self.name):
            raise SourceException(f"Source config {self.name} already exists")

        self.save()

    def delete(self):
        if not self.exists(self.name):
            raise SourceNotExists(f"Source config {self.name} doesn't exist")

        os.remove(self.file_path)

    @abstractmethod
    def prompt(self, default_config, advanced=False):
        pass

    def validate(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'json_schema_definitions', self.VALIDATION_SCHEMA_FILE_NAME)) as f:
            json_schema = json.load(f)

        validate(self.config, json_schema)

    def set_config(self, config):
        self.config = config

    def update_test_source_config(self, stage):
        for conf in stage['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]

    def create_test_pipeline(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines',
                               self.TEST_PIPELINE_NAME + '.json'), 'r') as f:
            data = json.load(f)

        pipeline_config = data['pipelineConfig']
        new_pipeline = api_client.create_pipeline(self.TEST_PIPELINE_NAME)
        self.update_test_source_config(pipeline_config['stages'][0])

        pipeline_config['uuid'] = new_pipeline['uuid']
        api_client.update_pipeline(self.TEST_PIPELINE_NAME, pipeline_config)

    def get_preview_data(self):
        self.create_test_pipeline()

        try:
            preview = api_client.create_preview(self.TEST_PIPELINE_NAME)
            preview_data = api_client.wait_for_preview(self.TEST_PIPELINE_NAME, preview['previewerId'])
        except Exception:
            api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
            raise
        api_client.delete_pipeline(self.TEST_PIPELINE_NAME)

        if not preview_data:
            raise SourceException('Connection error')

        return preview_data

    @if_validation_enabled
    def validate_connection(self):
        self.create_test_pipeline()
        try:
            validate_status = api_client.validate(self.TEST_PIPELINE_NAME)
            api_client.wait_for_preview(self.TEST_PIPELINE_NAME, validate_status['previewerId'])
        except Exception:
            api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
            raise
        api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
        print('Successfully connected to the source')
        return True

    def get_sample_records(self):
        preview_data = self.get_preview_data()

        if not preview_data:
            print('No preview data available')
            return

        try:
            data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
        except (ValueError, TypeError):
            print('No preview data available')
            return
        return [sdc_record_map_to_dict(record['value']) for record in data[:self.MAX_SAMPLE_RECORDS]]

    @abstractmethod
    def print_sample_data(self):
        pass


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass
