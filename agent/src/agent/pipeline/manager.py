import json
import logging
import click
import os
import shutil
import time
import agent.pipeline.config.handlers as config_handlers
import jsonschema

from agent import pipeline, destination
from agent.pipeline.config.validators import get_config_validator
from agent.pipeline import prompt, load_client_data
from agent import source
from agent.anodot_api_client import AnodotApiClient
from agent.constants import ERRORS_DIR, ENV_PROD, MONITORING_SOURCE_NAME
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.tools import print_json, sdc_record_map_to_dict, if_validation_enabled
from .. import proxy
from .pipeline import Pipeline, PipelineException
from agent.logger import get_logger
from typing import List


logger = get_logger(__name__)

LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.ERROR)]


class PipelineManager:
    def __init__(self, pipeline_obj: Pipeline):
        self.pipeline = pipeline_obj
        self.prompter = get_prompter(pipeline_obj.source.type)(self.pipeline)
        self.file_loader = get_file_loader(pipeline_obj.source.type)()
        self.sdc_creator = get_sdc_creator(pipeline_obj)

    def prompt(self, default_config, advanced=False):
        self.pipeline.set_config(self.prompter.prompt(default_config, advanced))

    def load_config(self, config, edit=False):
        self.pipeline.set_config(self.file_loader.load(config, edit))

    def validate_config(self):
        get_config_validator(self.pipeline).validate(self.pipeline)

    def create(self) -> Pipeline:
        try:
            pipeline_obj = api_client.create_pipeline(self.pipeline.name)
            new_config = self.sdc_creator.override_base_config(new_uuid=pipeline_obj['uuid'],
                                                               new_title=self.pipeline.name)
            api_client.update_pipeline(self.pipeline.name, new_config)
        except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
            delete(self.pipeline)
            raise pipeline.PipelineException(str(e))
        pipeline.repository.save(self.pipeline)
        return self.pipeline

    @if_validation_enabled
    def show_preview(self):
        try:
            preview = api_client.create_preview(self.pipeline.name)
            preview_data, errors = api_client.wait_for_preview(self.pipeline.name, preview['previewerId'])
        except StreamSetsApiClientException as e:
            print(str(e))
            return

        if preview_data['batchesOutput']:
            for output in preview_data['batchesOutput'][0]:
                if 'destination_OutputLane' in output['output']:
                    data = output['output']['destination_OutputLane'][:source.manager.MAX_SAMPLE_RECORDS]
                    if data:
                        print_json([sdc_record_map_to_dict(record['value']) for record in data])
                    else:
                        print('Could not fetch any data matching the provided config')
                    break
        else:
            print('Could not fetch any data matching the provided config')
        print(*errors, sep='\n')


def get_sdc_creator(pipeline_obj: Pipeline) -> config_handlers.base.BaseConfigHandler:
    handlers = {
        source.TYPE_MONITORING: config_handlers.monitoring.MonitoringConfigHandler,
        source.TYPE_INFLUX: config_handlers.influx.InfluxConfigHandler,
        source.TYPE_MONGO: config_handlers.mongo.MongoConfigHandler,
        source.TYPE_KAFKA: config_handlers.kafka.KafkaConfigHandler,
        source.TYPE_MYSQL: config_handlers.jdbc.JDBCConfigHandler,
        source.TYPE_POSTGRES: config_handlers.jdbc.JDBCConfigHandler,
        source.TYPE_ELASTIC: config_handlers.elastic.ElasticConfigHandler,
        source.TYPE_SPLUNK: config_handlers.tcp.TCPConfigHandler,
        source.TYPE_DIRECTORY: config_handlers.directory.DirectoryConfigHandler,
        source.TYPE_SAGE: config_handlers.sage.SageConfigHandler,
        source.TYPE_VICTORIA: config_handlers.victoria.VictoriaConfigHandler,
    }
    return handlers[pipeline_obj.source.type](pipeline_obj)


def get_file_loader(source_type: str):
    loaders = {
        source.TYPE_MONITORING: load_client_data.LoadClientData,
        source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
        source.TYPE_MONGO: load_client_data.MongoLoadClientData,
        source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
        source.TYPE_MYSQL: load_client_data.JDBCLoadClientData,
        source.TYPE_POSTGRES: load_client_data.JDBCLoadClientData,
        source.TYPE_ELASTIC: load_client_data.ElasticLoadClientData,
        source.TYPE_SPLUNK: load_client_data.TcpLoadClientData,
        source.TYPE_DIRECTORY: load_client_data.DirectoryLoadClientData,
        source.TYPE_SAGE: load_client_data.SageLoadClientData,
        source.TYPE_VICTORIA: load_client_data.VictoriaLoadClientData,
    }
    return loaders[source_type]


def get_prompter(source_type: str):
    prompters = {
        source.TYPE_MONITORING: prompt.PromptConfig,
        source.TYPE_INFLUX: prompt.PromptConfigInflux,
        source.TYPE_KAFKA: prompt.PromptConfigKafka,
        source.TYPE_MONGO: prompt.PromptConfigMongo,
        source.TYPE_MYSQL: prompt.PromptConfigJDBC,
        source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
        source.TYPE_ELASTIC: prompt.PromptConfigElastic,
        source.TYPE_SPLUNK: prompt.PromptConfigTCP,
        source.TYPE_DIRECTORY: prompt.PromptConfigDirectory,
        source.TYPE_SAGE: prompt.PromptConfigSage,
        source.TYPE_VICTORIA: prompt.PromptConfigVictoria,
    }
    return prompters[source_type]


def extract_configs(file):
    data = json.load(file)
    file.seek(0)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['pipeline_id']
        }
    }
    jsonschema.validate(data, json_schema)
    return data


def validate_configs_for_create(configs: dict):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'type': 'string', 'enum': source.repository.get_all_names()},
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['source', 'pipeline_id']
        }
    }
    jsonschema.validate(configs, json_schema)


def validate_config_for_create(config: dict):
    json_schema = {
        'type': 'object',
        'properties': {
            'source': {'type': 'string', 'enum': source.repository.get_all_names()},
            'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
        },
        'required': ['source', 'pipeline_id']
    }
    jsonschema.validate(config, json_schema)


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    pipeline_ = pipeline.Pipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get()
    )
    return pipeline_


def check_pipeline_id(pipeline_id: str):
    if pipeline.repository.exists(pipeline_id):
        raise PipelineException(f"Pipeline {pipeline_id} already exists")


def create_from_file(file):
    create_from_json(json.load(file))


def edit_using_file(file):
    edit_using_json(extract_configs(file))


def create_from_json(configs: dict) -> List[Pipeline]:
    validate_configs_for_create(configs)
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            check_pipeline_id(config['pipeline_id'])
            pipeline_ = create_pipeline_from_json(config)
            pipelines.append(pipeline_)
        except Exception as e:
            # todo traceback?
            exceptions[config['pipeline_id']] = str(e)
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def create_pipeline_from_json(config: dict) -> Pipeline:
    validate_config_for_create(config)
    pipeline_manager = PipelineManager(create_object(config['pipeline_id'], config['source']))
    pipeline_manager.load_config(config)
    pipeline_manager.validate_config()
    pipeline_manager.create()
    print(f'Pipeline {pipeline_manager.pipeline.name} created')
    return pipeline_manager.pipeline


def edit_using_json(configs: dict) -> List[Pipeline]:
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            pipelines.append(
                edit_pipeline_using_json(config)
            )
        except Exception as e:
            exceptions[config['pipeline_id']] = str(e)
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def edit_pipeline_using_json(config: dict) -> Pipeline:
    pipeline_manager = PipelineManager(pipeline.repository.get_by_name(config['pipeline_id']))
    pipeline_manager.load_config(config, edit=True)
    update(pipeline_manager.pipeline)
    return pipeline_manager.pipeline


def start(pipeline_obj: Pipeline):
    api_client.start_pipeline(pipeline_obj.name)
    wait_for_status(pipeline_obj.name, pipeline.Pipeline.STATUS_RUNNING)
    click.secho(f'{pipeline_obj.name} pipeline is running')
    if ENV_PROD:
        if wait_for_sending_data(pipeline_obj.name):
            click.secho(f'{pipeline_obj.name} pipeline is sending data')
        else:
            click.secho(f'{pipeline_obj.name} pipeline did not send any data')


def update(pipeline_obj: Pipeline):
    start_pipeline = False
    try:
        if get_pipeline_status(pipeline_obj.name) in [pipeline.Pipeline.STATUS_RUNNING, pipeline.Pipeline.STATUS_RETRY]:
            stop(pipeline_obj)
            start_pipeline = True

        api_pipeline = api_client.get_pipeline(pipeline_obj.name)
        new_config = get_sdc_creator(pipeline_obj)\
            .override_base_config(new_uuid=api_pipeline['uuid'], new_title=pipeline_obj.name)
        api_client.update_pipeline(pipeline_obj.name, new_config)

    except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
        raise pipeline.PipelineException(str(e))

    pipeline.repository.save(pipeline_obj)
    if start_pipeline:
        start(pipeline_obj)


def update_source_pipelines(source_: source.Source):
    for pipeline_ in pipeline.repository.get_by_source(source_.name):
        try:
            pipeline.manager.update(pipeline_)
        except pipeline.PipelineException as e:
            print(str(e))
            continue
        print(f'Pipeline {pipeline_.name} updated')


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
            logger.warning(f'Pipeline {pipeline_id} did not send any data. Received number of records - {stats["in"]}')
            return False
        print(f'Waiting for pipeline {pipeline_id} to send data. Check again after {delay} seconds...')
        time.sleep(delay)


def force_stop_pipeline(pipeline_id: str):
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException:
        pass

    if not check_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPING):
        raise pipeline.PipelineException("Can't force stop a pipeline not in the STOPPING state")

    api_client.force_stop_pipeline(pipeline_id)
    wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)


def stop(pipeline_obj: Pipeline):
    return stop_by_id(pipeline_obj.name)


def can_stop(pipeline_id: str) -> bool:
    return get_pipeline_status(pipeline_id) == Pipeline.STATUS_RUNNING


def stop_by_id(pipeline_id: str):
    print("Stopping the pipeline")
    api_client.stop_pipeline(pipeline_id)
    try:
        wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)
    except PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop_pipeline(pipeline_id)


def reset(pipeline_obj: Pipeline):
    try:
        api_client.reset_pipeline(pipeline_obj.name)
        get_sdc_creator(pipeline_obj).set_initial_offset()
    except (config_handlers.base.ConfigHandlerException, StreamSetsApiClientException) as e:
        raise pipeline.PipelineException(str(e))


def _delete_locally(pipeline_obj: Pipeline):
    if pipeline.repository.exists(pipeline_obj.name):
        pipeline.repository.delete_by_name(pipeline_obj.name)


def _delete_schema(pipeline_obj: Pipeline):
    if 'schema' in pipeline_obj.config:
        anodot_api_client = AnodotApiClient(pipeline_obj.destination.access_key,
                                            proxy.get_config(pipeline_obj.destination.proxy),
                                            base_url=pipeline_obj.destination.url)
        anodot_api_client.delete_schema(pipeline_obj.config['schema']['id'])


def _delete_from_streamsets(pipeline_id: str):
    if check_status(pipeline_id, pipeline.Pipeline.STATUS_RUNNING):
        stop_by_id(pipeline_id)
    api_client.delete_pipeline(pipeline_id)


def _cleanup_errors_dir(pipeline_id: str):
    errors_dir = os.path.join(ERRORS_DIR, pipeline_id)
    if os.path.isdir(errors_dir):
        shutil.rmtree(errors_dir)


def delete(pipeline_obj: Pipeline):
    _delete_schema(pipeline_obj)
    try:
        _delete_from_streamsets(pipeline_obj.name)
    except StreamSetsApiClientException as e:
        raise pipeline.PipelineException(str(e))
    _cleanup_errors_dir(pipeline_obj.name)
    _delete_locally(pipeline.repository.get_by_name(pipeline_obj.name))


def delete_by_id(pipeline_id: str):
    try:
        _delete_from_streamsets(pipeline_id)
    except StreamSetsApiClientException as e:
        raise pipeline.PipelineException(str(e))
    _cleanup_errors_dir(pipeline_id)
    if pipeline.repository.exists(pipeline_id):
        _delete_schema(pipeline.repository.get_by_name(pipeline_id))
        _delete_locally(pipeline.repository.get_by_name(pipeline_id))


def enable_destination_logs(pipeline_obj: Pipeline):
    pipeline_obj.destination.enable_logs()
    destination.repository.save(pipeline_obj.destination)
    update(pipeline_obj)


def disable_destination_logs(pipeline_obj: Pipeline):
    pipeline_obj.destination.disable_logs()
    destination.repository.save(pipeline_obj.destination)
    update(pipeline_obj)


def _update_stage_config(source_: source.Source, stage):
    for conf in stage['configuration']:
        if conf['name'] in source_.config:
            conf['value'] = source_.config[conf['name']]


def create_test_pipeline(source_: source.Source) -> str:
    with open(_get_test_pipeline_file_path(source_)) as f:
        pipeline_config = json.load(f)['pipelineConfig']
    _update_stage_config(source_, pipeline_config['stages'][0])
    test_pipeline_name = _get_test_pipeline_name(source_)

    new_pipeline = api_client.create_pipeline(test_pipeline_name)
    pipeline_config['uuid'] = new_pipeline['uuid']
    api_client.update_pipeline(test_pipeline_name, pipeline_config)
    return test_pipeline_name


def _get_test_pipeline_file_path(source_: source.Source) -> str:
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', _get_test_pipeline_file_name(source_) + '.json'
    )


def _get_test_pipeline_file_name(source_: source.Source) -> str:
    files = {
        source.TYPE_INFLUX: 'test_influx_qwe093',
        source.TYPE_MONGO: 'test_mongo_rand847',
        source.TYPE_KAFKA: 'test_kafka_kjeu4334',
        source.TYPE_MYSQL: 'test_jdbc_pdsf4587',
        source.TYPE_POSTGRES: 'test_jdbc_pdsf4587',
        source.TYPE_ELASTIC: 'test_elastic_asdfs3245',
        source.TYPE_SPLUNK: 'test_tcp_server_jksrj322',
        source.TYPE_DIRECTORY: 'test_directory_ksdjfjk21',
        source.TYPE_SAGE: 'test_sage_jfhdkj',
    }
    return files[source_.type]


def _get_test_pipeline_name(source_: source.Source) -> str:
    return _get_test_pipeline_file_name(source_) + source_.name


def start_monitoring_pipeline():
    if not source.repository.exists(MONITORING_SOURCE_NAME):
        source.repository.save(source.Source(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {}))
    pipeline_ = pipeline.manager.create_object(pipeline.MONITORING, MONITORING_SOURCE_NAME)
    pipeline_manager = pipeline.manager.PipelineManager(pipeline_)
    pipeline_manager.create()
    pipeline.manager.start(pipeline_)


def update_monitoring_pipeline():
    pipeline_ = pipeline.repository.get_by_name(pipeline.MONITORING)
    pipeline.manager.update(pipeline_)


class PipelineFreezeException(Exception):
    pass
