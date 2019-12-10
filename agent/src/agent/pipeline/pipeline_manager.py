import json
import os
import shutil

from .pipeline import Pipeline, PipelineException
from . import prompt, config_handlers, load_client_data
from .. import source
from agent.constants import ERRORS_DIR
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.tools import print_json, sdc_record_map_to_dict, if_validation_enabled

prompters = {
    source.TYPE_MONITORING: prompt.PromptConfig,
    source.TYPE_INFLUX: prompt.PromptConfigInflux,
    source.TYPE_KAFKA: prompt.PromptConfigKafka,
    source.TYPE_MONGO: prompt.PromptConfigMongo,
    source.TYPE_MYSQL: prompt.PromptConfigJDBC,
    source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
}

loaders = {
    source.TYPE_MONITORING: load_client_data.LoadClientData,
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


class PipelineManager:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.prompter = prompters[pipeline.source.type](self.pipeline)
        self.file_loader = loaders[pipeline.source.type]()
        self.sdc_creator = handlers[pipeline.source.type](self.pipeline)

    def prompt(self, default_config, advanced=False):
        self.pipeline.set_config(self.prompter.prompt(default_config, advanced))

    def load_config(self, config, edit=False):
        self.pipeline.set_config(self.file_loader.load(config, edit))

    def create(self):
        try:
            pipeline_obj = api_client.create_pipeline(self.pipeline.id)
            new_config = self.sdc_creator.override_base_config(self.pipeline.to_dict(), new_uuid=pipeline_obj['uuid'],
                                                               new_pipeline_title=self.pipeline.id)

            api_client.update_pipeline(self.pipeline.id, new_config)
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            self.delete()
            raise PipelineException(str(e))

        self.pipeline.save()

    def update(self):
        try:
            start_pipeline = False
            if self.pipeline.check_status(self.pipeline.STATUS_RUNNING):
                self.pipeline.stop()
                start_pipeline = True

            pipeline_obj = api_client.get_pipeline(self.pipeline.id)
            new_config = self.sdc_creator.override_base_config(self.pipeline.to_dict(), new_uuid=pipeline_obj['uuid'],
                                                               new_pipeline_title=self.pipeline.id)
            api_client.update_pipeline(self.pipeline.id, new_config)

            if start_pipeline:
                self.pipeline.start()
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))
        except config_handlers.ConfigHandlerException as e:
            self.delete()
            raise PipelineException(str(e))

        self.pipeline.save()

    def reset(self):
        try:
            api_client.reset_pipeline(self.pipeline.id)
            self.sdc_creator.set_initial_offset(self.pipeline.to_dict())
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))

    def delete(self):
        try:
            api_client.delete_pipeline(self.pipeline.id)
            if self.pipeline.exists(self.pipeline.id):
                os.remove(self.pipeline.file_path)
            errors_dir = os.path.join(ERRORS_DIR, self.pipeline.id)
            if os.path.isdir(errors_dir):
                shutil.rmtree(errors_dir)
        except StreamSetsApiClientException as e:
            raise PipelineException(str(e))

    @if_validation_enabled
    def show_preview(self):
        preview = api_client.create_preview(self.pipeline.id)
        preview_data = api_client.wait_for_preview(self.pipeline.id, preview['previewerId'])

        for output in preview_data['batchesOutput'][0]:
            if 'destination_OutputLane' not in output['output']:
                continue
            data = output['output']['destination_OutputLane'][:self.pipeline.source.MAX_SAMPLE_RECORDS]
            print_json([sdc_record_map_to_dict(record['value']) for record in data])

    def enable_destination_logs(self, enable):
        self.pipeline.destination.enable_logs(enable)
        self.update()
