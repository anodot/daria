import click
import os
import shutil
import time
import agent.pipeline.config.handlers as config_handlers

from . import pipeline
from agent.pipeline.config.validators import get_config_validator
from agent.pipeline import prompt, load_client_data
from .. import source, destination
from agent.anodot_api_client import AnodotApiClient
from agent.constants import ERRORS_DIR, ENV_PROD
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.tools import print_json, sdc_record_map_to_dict, if_validation_enabled
from .. import proxy
from ..repository import pipeline_repository, source_repository
from .pipeline import Pipeline, PipelineException
from jsonschema import validate


def validate_json_for_create(json: dict):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'type': 'string', 'enum': source_repository.get_all()},
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['source', 'pipeline_id']
        }
    }
    validate(json, json_schema)


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    return pipeline.Pipeline(
        pipeline_id,
        source_repository.get(source_name),
        {},
        destination.HttpDestination.get()
    )


def check_pipeline_id(pipeline_id: str):
    if pipeline_repository.exists(pipeline_id):
        raise PipelineException(f"Pipeline {pipeline_id} already exists")


def create_from_json(config: dict):
    check_pipeline_id(config['pipeline_id'])
    pipeline_manager = PipelineManager(create_object(config['pipeline_id'], config['source']))
    pipeline_manager.load_config(config)
    pipeline_manager.validate_config()
    pipeline_manager.create()


def edit_using_json(config: dict):
    pipeline_manager = PipelineManager(pipeline_repository.get(config['pipeline_id']))
    pipeline_manager.load_config(config, edit=True)
    pipeline_manager.update()


def start(pipeline_obj: Pipeline):
    api_client.start_pipeline(pipeline_obj.id)
    wait_for_status(pipeline_obj.id, pipeline.Pipeline.STATUS_RUNNING)
    click.secho(f'{pipeline_obj.id} pipeline is running')
    if ENV_PROD:
        wait_for_sending_data(pipeline_obj.id)
        click.secho(f'{pipeline_obj.id} pipeline is sending data')


def get_pipeline_status(pipeline_id: str) -> str:
    return api_client.get_pipeline_status(pipeline_id)['status']


def check_status(pipeline_id: str, status: str) -> bool:
    return get_pipeline_status(pipeline_id) == status


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
            raise pipeline.PipelineException(f"Pipeline {pipeline_id} has {stats['errors']} errors")
        delay = initial_delay ** i
        if i == tries:
            raise pipeline.PipelineException(
                f"Pipeline {pipeline_id} did not send any data. Received number of records - {stats['in']}")
        print(f'Waiting for pipeline {pipeline_id} to send data. Check again after {delay} seconds...')
        time.sleep(delay)


def force_stop_pipeline(pipeline_id: str):
    if not check_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPING):
        raise pipeline.PipelineException("Can't force stop a pipeline not in the STOPPING state")
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException:
        pass

    if not check_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPING):
        raise pipeline.PipelineException("Can't force stop a pipeline not in the STOPPING state")

    api_client.force_stop_pipeline(pipeline_id)
    wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)


def stop_pipeline(pipeline_id: str):
    print("Stopping the pipeline")
    api_client.stop_pipeline(pipeline_id)
    try:
        wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)
    except PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop_pipeline(pipeline_id)


def delete_pipeline(pipeline_id: str):
    try:
        if check_status(pipeline_id, pipeline.Pipeline.STATUS_RUNNING):
            stop_pipeline(pipeline_id)

        api_client.delete_pipeline(pipeline_id)
        if pipeline_repository.exists(pipeline_id):
            pipeline_repository.delete_by_id(pipeline_id)
        errors_dir = os.path.join(ERRORS_DIR, pipeline_id)
        if os.path.isdir(errors_dir):
            shutil.rmtree(errors_dir)
    except StreamSetsApiClientException as e:
        raise pipeline.PipelineException(str(e))


class PipelineManager:
    def __init__(self, pipeline_obj: Pipeline):
        # todo moved it here in order to avoid circular imports, refactor
        prompters = {
            source.TYPE_MONITORING: prompt.PromptConfig,
            source.TYPE_INFLUX: prompt.PromptConfigInflux,
            source.TYPE_KAFKA: prompt.PromptConfigKafka,
            source.TYPE_MONGO: prompt.PromptConfigMongo,
            source.TYPE_MYSQL: prompt.PromptConfigJDBC,
            source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
            source.TYPE_ELASTIC: prompt.PromptConfigElastic,
            source.TYPE_SPLUNK: prompt.PromptConfigTCP,
            source.TYPE_DIRECTORY: prompt.PromptConfigDirectory
        }

        loaders = {
            source.TYPE_MONITORING: load_client_data.LoadClientData,
            source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
            source.TYPE_MONGO: load_client_data.MongoLoadClientData,
            source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
            source.TYPE_MYSQL: load_client_data.JDBCLoadClientData,
            source.TYPE_POSTGRES: load_client_data.JDBCLoadClientData,
            source.TYPE_ELASTIC: load_client_data.ElasticLoadClientData,
            source.TYPE_SPLUNK: load_client_data.TcpLoadClientData,
            source.TYPE_DIRECTORY: load_client_data.DirectoryLoadClientData
        }

        handlers = {
            source.TYPE_MONITORING: config_handlers.monitoring.MonitoringConfigHandler,
            source.TYPE_INFLUX: config_handlers.influx.InfluxConfigHandler,
            source.TYPE_MONGO: config_handlers.mongo.MongoConfigHandler,
            source.TYPE_KAFKA: config_handlers.kafka.KafkaConfigHandler,
            source.TYPE_MYSQL: config_handlers.jdbc.JDBCConfigHandler,
            source.TYPE_POSTGRES: config_handlers.jdbc.JDBCConfigHandler,
            source.TYPE_ELASTIC: config_handlers.elastic.ElasticConfigHandler,
            source.TYPE_SPLUNK: config_handlers.tcp.TCPConfigHandler,
            source.TYPE_DIRECTORY: config_handlers.directory.DirectoryConfigHandler
        }
        self.pipeline = pipeline_obj
        self.prompter = prompters[pipeline_obj.source.type](self.pipeline)
        self.file_loader = loaders[pipeline_obj.source.type]()
        self.sdc_creator = handlers[pipeline_obj.source.type](self.pipeline)

    def prompt(self, default_config, advanced=False):
        self.pipeline.set_config(self.prompter.prompt(default_config, advanced))

    def load_config(self, config, edit=False):
        self.pipeline.set_config(self.file_loader.load(config, edit))

    def validate_config(self):
        get_config_validator(self.pipeline).validate(self.pipeline)

    def create(self):
        try:
            pipeline_obj = api_client.create_pipeline(self.pipeline.id)
            new_config = self.sdc_creator.override_base_config(new_uuid=pipeline_obj['uuid'],
                                                               new_title=self.pipeline.id)

            api_client.update_pipeline(self.pipeline.id, new_config)
        except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
            self.delete()
            raise pipeline.PipelineException(str(e))

        pipeline_repository.save(self.pipeline)

    def update(self):
        start_pipeline = False
        try:
            if get_pipeline_status(self.pipeline.id) in [pipeline.Pipeline.STATUS_RUNNING, pipeline.Pipeline.STATUS_RETRY]:
                self.stop()
                start_pipeline = True

            pipeline_obj = api_client.get_pipeline(self.pipeline.id)
            new_config = self.sdc_creator.override_base_config(new_uuid=pipeline_obj['uuid'],
                                                               new_title=self.pipeline.id)
            api_client.update_pipeline(self.pipeline.id, new_config)

        except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise pipeline.PipelineException(str(e))

        pipeline_repository.save(self.pipeline)
        if start_pipeline:
            self.start()

    def reset(self):
        try:
            api_client.reset_pipeline(self.pipeline.id)
            self.sdc_creator.set_initial_offset()
        except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
            raise pipeline.PipelineException(str(e))

    def delete(self):
        if 'schema' in self.pipeline.config:
            anodot_api_client = AnodotApiClient(self.pipeline.destination.access_key,
                                                proxy.get_config(self.pipeline.destination.proxy),
                                                base_url=self.pipeline.destination.url)
            anodot_api_client.delete_schema(self.pipeline.config['schema']['id'])
        delete_pipeline(self.pipeline.id)

    def enable_destination_logs(self, enable):
        self.pipeline.destination.enable_logs(enable)
        self.update()

    def stop(self):
        stop_pipeline(self.pipeline.id)

    def start(self):
        api_client.start_pipeline(self.pipeline.id)
        wait_for_status(self.pipeline.id, pipeline.Pipeline.STATUS_RUNNING)
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

        if not preview_data['batchesOutput']:
            print('Could not fetch any data matching the provided config')
            return

        for output in preview_data['batchesOutput'][0]:
            if 'destination_OutputLane' in output['output']:
                data = output['output']['destination_OutputLane'][:source.Source.MAX_SAMPLE_RECORDS]
                if data:
                    print_json([sdc_record_map_to_dict(record['value']) for record in data])
                else:
                    print('Could not fetch any data matching the provided config')
                break


class PipelineFreezeException(Exception):
    pass
