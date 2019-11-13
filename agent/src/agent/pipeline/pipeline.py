import json
import os
import shutil
import time

from .. import source
from agent.constants import DATA_DIR, ERRORS_DIR
from agent.destination import HttpDestination
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from . import prompt, config_handlers, load_client_data


class Pipeline:
    DIR = os.path.join(DATA_DIR, 'pipelines')
    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'

    def __init__(self, pipeline_id: str,
                 source_obj: source.Source,
                 config: dict,
                 destination: HttpDestination,
                 config_handler: config_handlers.BaseConfigHandler,
                 prompter: prompt.PromptConfig,
                 loader: load_client_data.LoadClientData):
        self.id = pipeline_id
        self.config = config
        self.source = source_obj
        self.destination = destination
        self.config_handler = config_handler
        self.prompter = prompter
        self.loader = loader

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.id)

    def to_dict(self):
        return {
            **self.config,
            'pipeline_id': self.id,
            'source': self.source.to_dict() if self.source else None,
            'destination': self.destination.to_dict()
        }

    @classmethod
    def get_file_path(cls, pipeline_id: str) -> str:
        return os.path.join(cls.DIR, pipeline_id + '.json')

    @classmethod
    def exists(cls, pipeline_id: str) -> bool:
        return os.path.isfile(cls.get_file_path(pipeline_id))

    def set_config(self, config: dict):
        self.config.update(config)

    # def load(self):
    #     if not self.exists():
    #         raise PipelineNotExists(f"Pipeline {self.id} doesn't exist")
    #
    #     with open(self.file_path, 'r') as f:
    #         self.config = json.load(f)
    #
    #     self.source = source.load_object(self.config['source']['name'])
    #     # self.config['source'] = self.source.to_dict()
    #     # self.config['destination'] = self.destination.load()
    #
    #     return self.config

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    # def prompt(self, default_config=None, advanced=False):
    #     if not default_config:
    #         default_config = self.to_dict()
    #     self.config.update(self.prompters[self.source.type](default_config, advanced).config)
    #
    # def load_client_data(self, client_config, edit=False):
    #     self.config.update(self.loaders[self.source.type](client_config, edit).load())
    #
    # def get_config_handler(self, pipeline_obj=None) -> config_handlers.BaseConfigHandler:
    #     return self.handlers[self.source.type](self.to_dict(), pipeline_obj)

    def create(self):
        try:
            pipeline_obj = api_client.create_pipeline(self.id)
            new_config = self.config_handler.override_base_config(self.to_dict(), new_uuid=pipeline_obj['uuid'])

            api_client.update_pipeline(self.id, new_config)
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            self.delete()
            raise PipelineException(str(e))

        self.save()

    def update(self):
        try:
            pipeline_obj = api_client.get_pipeline(self.id)
            new_config = self.config_handler.override_base_config(self.to_dict(), base_config=pipeline_obj)

            api_client.update_pipeline(self.id, new_config)
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))
        except config_handlers.ConfigHandlerException as e:
            self.delete()
            raise PipelineException(str(e))

        self.save()

    def reset(self):
        try:
            api_client.reset_pipeline(self.id)
            self.config_handler.set_initial_offset()
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))

    def delete(self):
        try:
            api_client.delete_pipeline(self.id)
            if self.exists(self.id):
                os.remove(self.file_path)
            errors_dir = os.path.join(ERRORS_DIR, self.id)
            if os.path.isdir(errors_dir):
                shutil.rmtree(errors_dir)
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))

    def enable_destination_logs(self, enable):
        self.destination.enable_logs(enable)
        self.update()

    def wait_for_status(self, status, tries=5, initial_delay=3):
        for i in range(1, tries):
            response = api_client.get_pipeline_status(self.id)
            if response['status'] == status:
                return True
            delay = initial_delay ** i
            if i == tries:
                raise PipelineException(f"Pipeline {self.id} is still {response['status']} after {tries} tries")
            print(f"Pipeline {self.id} is {response['status']}. Check again after {delay} seconds...")
            time.sleep(delay)

    def wait_for_sending_data(self, tries=5, initial_delay=2):
        for i in range(1, tries + 1):
            response = api_client.get_pipeline_metrics(self.id)
            stats = {
                'in': response['counters']['pipeline.batchInputRecords.counter']['count'],
                'out': response['counters']['pipeline.batchOutputRecords.counter']['count'],
                'errors': response['counters']['pipeline.batchErrorRecords.counter']['count'],
            }
            if stats['out'] > 0 and stats['errors'] == 0:
                return True
            if stats['errors'] > 0:
                raise PipelineException(f"Pipeline {self.id} is has {stats['errors']} errors")
            delay = initial_delay ** i
            if i == tries:
                raise PipelineException(f"Pipeline {self.id} did not send any data. Received number of records - {stats['in']}")
            print(f'Waiting for pipeline {self.id} to send data. Check again after {delay} seconds...')
            time.sleep(delay)

    def stop(self):
        api_client.stop_pipeline(self.id)
        self.wait_for_status(self.STATUS_STOPPED)

    def start(self):
        api_client.start_pipeline(self.id)
        self.wait_for_status(self.STATUS_RUNNING)


class PipelineException(Exception):
    pass


class PipelineNotExists(PipelineException):
    pass
