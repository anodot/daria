import json
import os
import shutil

from agent.constants import DATA_DIR, ERRORS_DIR
from agent.destination import HttpDestination
from agent.source import Source
from agent.streamsets_api_client import api_client, StreamSetsApiClientException

from . import prompt, config_handlers, load_client_data


class Pipeline:
    DIR = os.path.join(DATA_DIR, 'pipelines')

    prompters = {
        Source.TYPE_INFLUX: prompt.PromptConfigInflux,
        Source.TYPE_KAFKA: prompt.PromptConfigKafka,
        Source.TYPE_MONGO: prompt.PromptConfigMongo,
    }

    loaders = {
        Source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
        Source.TYPE_MONGO: load_client_data.MongoLoadClientData,
        Source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
    }

    config_handlers = {
        Source.TYPE_INFLUX: config_handlers.InfluxConfigHandler,
        Source.TYPE_MONGO: config_handlers.JsonConfigHandler,
        Source.TYPE_KAFKA: config_handlers.KafkaConfigHandler,
        Source.TYPE_MONITORING: config_handlers.MonitoringConfigHandler,
    }

    def __init__(self, pipeline_id, source_name=None):
        self.source = Source(source_name).load() if source_name else None
        self.destination = HttpDestination()
        self.config = {
            'pipeline_id': pipeline_id,
            'source': self.source,
            'destination': self.destination.load()
        }

    @property
    def file_path(self):
        return os.path.join(self.DIR, self.id + '.json')

    @property
    def source_type(self):
        if self.id == 'Monitoring':
            return Source.TYPE_MONITORING
        return self.config['source']['type']

    @property
    def id(self):
        return self.config['pipeline_id']

    def exists(self):
        return os.path.isfile(self.file_path)

    def load(self):
        if not self.exists():
            raise PipelineNotExists(f"Pipeline {self.id} doesn't exist")

        with open(self.file_path, 'r') as f:
            self.config = json.load(f)

        return self.config

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.config, f)

    def prompt(self, default_config=None, advanced=False):
        if not default_config:
            default_config = self.config
        self.config.update(self.prompters[self.source_type](default_config, advanced).config)

    def load_client_data(self, client_config, edit=False):
        self.config.update(self.loaders[self.source_type](client_config, self.source_type, edit).load())

    def get_config_handler(self, pipeline_obj=None):
        return self.config_handlers[self.source_type](self.config, pipeline_obj)

    def create(self):
        try:
            pipeline_obj = api_client.create_pipeline(self.id)
            config_handler = self.get_config_handler()
            new_config = config_handler.override_base_config(pipeline_obj['uuid'], pipeline_obj['title'])

            api_client.update_pipeline(self.id, new_config)
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))

        self.save()

    def update(self):
        try:
            pipeline_obj = api_client.get_pipeline(self.id)
            config_handler = self.get_config_handler(pipeline_obj)
            new_config = config_handler.override_base_config()

            api_client.update_pipeline(self.id, new_config)
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
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
            os.remove(self.file_path)
            errors_dir = os.path.join(ERRORS_DIR, self.id)
            if os.path.isdir(errors_dir):
                shutil.rmtree(errors_dir)
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))

    def enable_destination_logs(self, enable):
        self.destination.enable_logs(enable)
        self.config['destination'] = self.destination.config
        self.update()


class PipelineException(Exception):
    pass


class PipelineNotExists(PipelineException):
    pass
