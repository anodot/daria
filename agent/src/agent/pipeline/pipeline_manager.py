import click
import os
import shutil
import time

from .pipeline import Pipeline, PipelineException
from . import prompt, config_handlers, load_client_data
from .. import source
from agent.constants import ERRORS_DIR, ENV_PROD
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.tools import print_json, sdc_record_map_to_dict, if_validation_enabled

prompters = {
    source.TYPE_MONITORING: prompt.PromptConfig,
    source.TYPE_INFLUX: prompt.PromptConfigInflux,
    source.TYPE_KAFKA: prompt.PromptConfigKafka,
    source.TYPE_MONGO: prompt.PromptConfigMongo,
    source.TYPE_MYSQL: prompt.PromptConfigJDBC,
    source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
    source.TYPE_ELASTIC: prompt.PromptConfigElastic,
}

loaders = {
    source.TYPE_MONITORING: load_client_data.LoadClientData,
    source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
    source.TYPE_MONGO: load_client_data.MongoLoadClientData,
    source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
    source.TYPE_MYSQL: load_client_data.JDBCLoadClientData,
    source.TYPE_POSTGRES: load_client_data.JDBCLoadClientData,
    source.TYPE_ELASTIC: load_client_data.ElasticLoadClientData,
}

handlers = {
    source.TYPE_MONITORING: config_handlers.MonitoringConfigHandler,
    source.TYPE_INFLUX: config_handlers.InfluxConfigHandler,
    source.TYPE_MONGO: config_handlers.MongoConfigHandler,
    source.TYPE_KAFKA: config_handlers.KafkaConfigHandler,
    source.TYPE_MYSQL: config_handlers.JDBCConfigHandler,
    source.TYPE_POSTGRES: config_handlers.JDBCConfigHandler,
    source.TYPE_ELASTIC: config_handlers.ElasticConfigHandler,
}


def check_status(pipeline_id: str, status: str):
    response = api_client.get_pipeline_status(pipeline_id)
    return response['status'] == status


def wait_for_status(pipeline_id: str, status: str, tries: int = 5, initial_delay: int = 3):
    for i in range(1, tries + 1):
        response = api_client.get_pipeline_status(pipeline_id)
        if response['status'] == status:
            return True
        delay = initial_delay ** i
        if i == tries:
            raise PipelineFreezeException(f"Pipeline {pipeline_id} is still {response['status']} after {tries} tries")
        print(f"Pipeline {pipeline_id} is {response['status']}. Check again after {delay} seconds...")
        time.sleep(delay)


def wait_for_sending_data(pipeline_id: str, tries: int = 5, initial_delay: int = 2):
    for i in range(1, tries + 1):
        response = api_client.get_pipeline_metrics(pipeline_id)
        stats = {
            'in': response['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': response['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': response['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        if stats['out'] > 0 and stats['errors'] == 0:
            return True
        if stats['errors'] > 0:
            raise PipelineException(f"Pipeline {pipeline_id} is has {stats['errors']} errors")
        delay = initial_delay ** i
        if i == tries:
            raise PipelineException(f"Pipeline {pipeline_id} did not send any data. Received number of records - {stats['in']}")
        print(f'Waiting for pipeline {pipeline_id} to send data. Check again after {delay} seconds...')
        time.sleep(delay)


def force_stop_pipeline(pipeline_id: str):
    if not check_status(pipeline_id, Pipeline.STATUS_STOPPING):
        raise PipelineException("Can't force stop a pipeline not in the STOPPING state")

    api_client.force_stop_pipeline(pipeline_id)
    wait_for_status(pipeline_id, Pipeline.STATUS_STOPPED)


def stop_pipeline(pipeline_id: str):
    print("Stopping the pipeline")
    api_client.stop_pipeline(pipeline_id)
    try:
        wait_for_status(pipeline_id, Pipeline.STATUS_STOPPED)
    except PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop_pipeline(pipeline_id)


def delete_pipeline(pipeline_id: str):
    try:
        if check_status(pipeline_id, Pipeline.STATUS_RUNNING):
            stop_pipeline(pipeline_id)

        api_client.delete_pipeline(pipeline_id)
        if Pipeline.exists(pipeline_id):
            os.remove(Pipeline.get_file_path(pipeline_id))
        errors_dir = os.path.join(ERRORS_DIR, pipeline_id)
        if os.path.isdir(errors_dir):
            shutil.rmtree(errors_dir)
    except StreamSetsApiClientException as e:
        raise PipelineException(str(e))


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
        start_pipeline = False
        try:
            if check_status(self.pipeline.id, Pipeline.STATUS_RUNNING):
                self.stop()
                start_pipeline = True

            pipeline_obj = api_client.get_pipeline(self.pipeline.id)
            new_config = self.sdc_creator.override_base_config(self.pipeline.to_dict(), new_uuid=pipeline_obj['uuid'],
                                                               new_pipeline_title=self.pipeline.id)
            api_client.update_pipeline(self.pipeline.id, new_config)

        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))
        finally:
            if start_pipeline:
                self.start()

        self.pipeline.save()

    def reset(self):
        try:
            api_client.reset_pipeline(self.pipeline.id)
            self.sdc_creator.set_initial_offset(self.pipeline.to_dict())
        except (config_handlers.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise PipelineException(str(e))

    def delete(self):
        delete_pipeline(self.pipeline.id)

    def enable_destination_logs(self, enable):
        self.pipeline.destination.enable_logs(enable)
        self.update()

    def stop(self):
        stop_pipeline(self.pipeline.id)

    def start(self):
        api_client.start_pipeline(self.pipeline.id)
        wait_for_status(self.pipeline.id, Pipeline.STATUS_RUNNING)
        click.secho(f'{self.pipeline.id} pipeline is running')
        if ENV_PROD:
            wait_for_sending_data(self.pipeline.id)
            click.secho(f'{self.pipeline.id} pipeline is sending data')

    @if_validation_enabled
    def show_preview(self):
        try:
            preview = api_client.create_preview(self.pipeline.id)
            preview_data = api_client.wait_for_preview(self.pipeline.id, preview['previewerId'])
        except StreamSetsApiClientException as e:
            print(str(e))
            return

        for output in preview_data['batchesOutput'][0]:
            if 'destination_OutputLane' in output['output']:
                data = output['output']['destination_OutputLane'][:source.Source.MAX_SAMPLE_RECORDS]
                if data:
                    print_json([sdc_record_map_to_dict(record['value']) for record in data])
                else:
                    print('Could not fetch any data matching the provided config')
                break


class PipelineFreezeException(PipelineException):
    pass
