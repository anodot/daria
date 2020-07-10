import click
import json
import os

from abc import ABC, abstractmethod
from agent import source
from agent.tools import if_validation_enabled, sdc_record_map_to_dict
from agent.streamsets_api_client import api_client
from agent.logger import get_logger


logger = get_logger(__name__)


class Builder(ABC):
    def __init__(self, source_name: str, source_type: str):
        self.source = source.Source(source_name, source_type, {})
        self.sample_data = None

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass

    @abstractmethod
    def validate(self):
        pass

    # todo refactor children
    def set_config(self, config):
        self.source.config = config

    # todo
    def update_test_source_config(self, stage):
        for conf in stage['configuration']:
            if conf['name'] in self.source.config:
                conf['value'] = self.source.config[conf['name']]

    # todo move pipeline creation out of source package
    def create_test_pipeline(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines',
                               self.TEST_PIPELINE_FILENAME + '.json')) as f:
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

    # todo
    @if_validation_enabled
    def validate_connection(self):
        self.create_test_pipeline()
        try:
            validate_status = api_client.validate(self.test_pipeline_name)
            api_client.wait_for_preview(self.test_pipeline_name, validate_status['previewerId'])
        except Exception:
            api_client.delete_pipeline(self.test_pipeline_name)
            raise
        finally:
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
        return [sdc_record_map_to_dict(record['value']) for record in data[:source.manager.MAX_SAMPLE_RECORDS]]

    @abstractmethod
    def print_sample_data(self):
        pass


# todo
class SourceException(click.ClickException):
    pass


class SourceNotExists(SourceException):
    pass


class SourceConfigDeprecated(SourceException):
    pass
