import click
import json
import os

from abc import ABC, abstractmethod
from agent import pipeline
from agent.constants import DATA_DIR
from agent.tools import if_validation_enabled, sdc_record_map_to_dict
from jsonschema import validate
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.logger import get_logger


logger = get_logger(__name__)


class Source(ABC):
    VALIDATION_SCHEMA_FILE_NAME = ''
    TEST_PIPELINE_FILENAME = ''
    DIR = os.path.join(DATA_DIR, 'sources')
    MAX_SAMPLE_RECORDS = 3

    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None
        self.test_pipeline_name = self.TEST_PIPELINE_FILENAME + self.name

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

    @classmethod
    def delete_source(cls, source_name):
        if not cls.exists(source_name):
            raise SourceNotExists(f"Source config {source_name} doesn't exist")

        pipelines = pipeline.get_pipelines(source_name=source_name)
        if pipelines:
            raise SourceException(f"Can't delete. Source is used by {', '.join([p.id for p in pipelines])} pipelines")

        os.remove(cls.get_file_path(source_name))

    def delete(self):
        self.delete_source(self.name)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> dict:
        pass

    @abstractmethod
    def validate(self):
        pass

    def validate_json(self):
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
                               self.TEST_PIPELINE_FILENAME + '.json'), 'r') as f:
            data = json.load(f)

        pipeline_config = data['pipelineConfig']
        new_pipeline = api_client.create_pipeline(self.test_pipeline_name)
        self.update_test_source_config(pipeline_config['stages'][0])

        pipeline_config['uuid'] = new_pipeline['uuid']
        api_client.update_pipeline(self.test_pipeline_name, pipeline_config)

    def get_preview_data(self):
        self.create_test_pipeline()

        try:
            preview = api_client.create_preview(self.test_pipeline_name)
            preview_data = api_client.wait_for_preview(self.test_pipeline_name, preview['previewerId'])
        except (Exception, KeyboardInterrupt) as e:
            logger.exception(str(e))
            api_client.delete_pipeline(self.test_pipeline_name)
            raise
        api_client.delete_pipeline(self.test_pipeline_name)

        return preview_data

    @if_validation_enabled
    def validate_connection(self):
        self.create_test_pipeline()
        try:
            validate_status = api_client.validate(self.test_pipeline_name)
            api_client.wait_for_preview(self.test_pipeline_name, validate_status['previewerId'])
        except Exception:
            api_client.delete_pipeline(self.test_pipeline_name)
            raise
        api_client.delete_pipeline(self.test_pipeline_name)
        print('Successfully connected to the source')
        return True

    def get_sample_records(self):
        preview_data = self.get_preview_data()

        if not preview_data:
            print('No preview data available')
            return

        try:
            data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
        except (ValueError, TypeError, IndexError) as e:
            logger.exception(str(e))
            print('No preview data available')
            return
        return [sdc_record_map_to_dict(record['value']) for record in data[:self.MAX_SAMPLE_RECORDS]]

    @abstractmethod
    def print_sample_data(self):
        pass


class SourceException(click.ClickException):
    pass


class SourceNotExists(SourceException):
    pass


class SourceConfigDeprecated(SourceException):
    pass
