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

    prompters = {
        source.TYPE_INFLUX: prompt.PromptConfigInflux,
        source.TYPE_KAFKA: prompt.PromptConfigKafka,
        source.TYPE_MONGO: prompt.PromptConfigMongo,
        source.TYPE_MYSQL: prompt.PromptConfigJDBC,
        source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
    }

    loaders = {
        source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
        source.TYPE_MONGO: load_client_data.MongoLoadClientData,
        source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
        source.TYPE_MYSQL: load_client_data.JDBCLoadClientData,
        source.TYPE_POSTGRES: load_client_data.JDBCLoadClientData,
    }

    handlers = {
        source.TYPE_MONITORING: config_handlers.MonitoringConfigHandler,
        source.TYPE_INFLUX: config_handlers.InfluxConfigHandler,
        source.TYPE_MONGO: config_handlers.MongoConfigHandler,
        source.TYPE_KAFKA: config_handlers.KafkaConfigHandler,
        source.TYPE_MYSQL: config_handlers.JDBCConfigHandler,
        source.TYPE_POSTGRES: config_handlers.JDBCConfigHandler
    }

    def __init__(self, pipeline_id, source_name=None):
        self.source = source.load_object(source_name) if source_name else None
        self.destination = HttpDestination()
        self.destination.load()
        self.id = pipeline_id
        self.config = {}

    @classmethod
    def create_dir(cls):
        if not os.path.exists(cls.DIR):
            os.mkdir(cls.DIR)

    @property
    def file_path(self):
        return os.path.join(self.DIR, self.id + '.json')

    def to_dict(self):
        return {
            **self.config,
            'pipeline_id': self.id,
            'source': self.source.to_dict() if self.source else None,
            'destination': self.destination.to_dict()
        }

    def exists(self):
        return os.path.isfile(self.file_path)

    def load(self):
        if not self.exists():
            raise PipelineNotExists(f"Pipeline {self.id} doesn't exist")

        with open(self.file_path, 'r') as f:
            self.config = json.load(f)

        self.source = source.load_object(self.config['source']['name'])
        # self.config['source'] = self.source.to_dict()
        # self.config['destination'] = self.destination.load()

        return self.config

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def prompt(self, default_config=None, advanced=False):
        if not default_config:
            default_config = self.to_dict()
        self.config.update(self.prompters[self.source.type](default_config, advanced).config)

    def load_client_data(self, client_config, edit=False):
        self.config.update(self.loaders[self.source.type](client_config, edit).load())

    def get_config_handler(self, pipeline_obj=None) -> config_handlers.BaseConfigHandler:
        return self.handlers[self.source.type](self.to_dict(), pipeline_obj)

    def create(self):
        try:
            pipeline_obj = api_client.create_pipeline(self.id)
            config_handler = self.get_config_handler()
            new_config = config_handler.override_base_config(pipeline_obj['uuid'], pipeline_obj['title'])

            api_client.update_pipeline(self.id, new_config)
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            self.delete()
            raise PipelineException(str(e))

        self.save()

    def update(self):
        try:
            pipeline_obj = api_client.get_pipeline(self.id)
            config_handler = self.get_config_handler(pipeline_obj)
            new_config = config_handler.override_base_config()

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
            config_handler = self.get_config_handler()
            config_handler.set_initial_offset()
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))

    def delete(self):
        try:
            api_client.delete_pipeline(self.id)
            if self.exists():
                os.remove(self.file_path)
            errors_dir = os.path.join(ERRORS_DIR, self.id)
            if os.path.isdir(errors_dir):
                shutil.rmtree(errors_dir)
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))

    def enable_destination_logs(self, enable):
        self.destination.enable_logs(enable)
        # self.config['destination'] = self.destination.to_dict()
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
