import json
import logging
import click
import os
import time
import agent.pipeline.config.handlers as config_handlers
import jsonschema

from agent import source, pipeline, destination
from agent.pipeline.config import schema
from agent.pipeline.config.validators import get_config_validator
from agent.pipeline import prompt, load_client_data, Pipeline
from agent.destination import anodot_api_client
from agent.modules.constants import ENV_PROD, MONITORING_SOURCE_NAME
from agent.modules import streamsets_api_client
from agent.modules.tools import print_json, sdc_record_map_to_dict
from agent.modules.logger import get_logger
from typing import List
from copy import deepcopy

logger = get_logger(__name__)

LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.ERROR)]


class PipelineBuilder:
    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.prompter = get_prompter(pipeline_.source.type)(self.pipeline)
        self.file_loader = get_file_loader(pipeline_.source.type)()

    def prompt(self, default_config, advanced=False):
        self.pipeline.set_config(self.prompter.prompt(default_config, advanced))

    def load_config(self, config, edit=False):
        self.pipeline.set_config(self.file_loader.load(config, edit))
        self.validate_config()

    def validate_config(self):
        get_config_validator(self.pipeline).validate(self.pipeline)


def show_preview(pipeline_: Pipeline):
    try:
        preview = streamsets_api_client.api_client.create_preview(pipeline_.name)
        preview_data, errors = streamsets_api_client.api_client.wait_for_preview(pipeline_.name, preview['previewerId'])
    except streamsets_api_client.StreamSetsApiClientException as e:
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


def get_sdc_creator(pipeline_: Pipeline, is_preview=False) -> config_handlers.base.BaseConfigHandler:
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
    return handlers[pipeline_.source.type](pipeline_, is_preview)


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


def validate_configs_for_create(configs: list):
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
        raise pipeline.PipelineException(f"Pipeline {pipeline_id} already exists")


def create_from_file(file):
    create_from_json(json.load(file))


def edit_using_file(file):
    edit_using_json(extract_configs(file))


def create_from_json(configs: list) -> List[Pipeline]:
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
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {str(e)}'
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def create_pipeline_from_json(config: dict) -> Pipeline:
    validate_config_for_create(config)
    pipeline_builder = PipelineBuilder(create_object(config['pipeline_id'], config['source']))
    pipeline_builder.load_config(config)
    create(pipeline_builder.pipeline)
    print(f'Pipeline {pipeline_builder.pipeline.name} created')
    return pipeline_builder.pipeline


def edit_using_json(configs: list) -> List[Pipeline]:
    if not isinstance(configs, list):
        raise ValueError(f'Provided data must be a list of configs, {type(configs).__name__} provided instead')
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            pipelines.append(
                edit_pipeline_using_json(config)
            )
        except Exception as e:
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {str(e)}'
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def edit_pipeline_using_json(config: dict) -> Pipeline:
    pipeline_builder = PipelineBuilder(pipeline.repository.get_by_name(config['pipeline_id']))
    pipeline_builder.load_config(config, edit=True)
    update(pipeline_builder.pipeline)
    return pipeline_builder.pipeline


def start(pipeline_: Pipeline):
    streamsets_api_client.api_client.start_pipeline(pipeline_.name)
    wait_for_status(pipeline_.name, pipeline.Pipeline.STATUS_RUNNING)
    click.secho(f'{pipeline_.name} pipeline is running')
    if ENV_PROD:
        if wait_for_sending_data(pipeline_.name):
            click.secho(f'{pipeline_.name} pipeline is sending data')
        else:
            click.secho(f'{pipeline_.name} pipeline did not send any data')


def create(pipeline_: Pipeline):
    _create_in_streamsets(pipeline_)
    pipeline.repository.save(pipeline_)


def _create_in_streamsets(pipeline_: Pipeline):
    try:
        streamsets_pipeline = streamsets_api_client.api_client.create_pipeline(pipeline_.name)
        new_config = get_sdc_creator(pipeline_)\
            .override_base_config(new_uuid=streamsets_pipeline['uuid'], new_title=pipeline_.name)
        streamsets_api_client.api_client.update_pipeline(pipeline_.name, new_config)
    except (config_handlers.base.ConfigHandlerException, streamsets_api_client.StreamSetsApiClientException) as e:
        try:
            _delete_from_streamsets(pipeline_.name)
        except streamsets_api_client.StreamSetsApiClientException:
            # ignore if it doesn't exist in streamsets
            pass
        raise pipeline.PipelineException(str(e))


def update(pipeline_: Pipeline):
    start_pipeline = False
    try:
        if get_pipeline_status(pipeline_.name) in [pipeline.Pipeline.STATUS_RUNNING, pipeline.Pipeline.STATUS_RETRY]:
            stop(pipeline_)
            start_pipeline = True
        api_pipeline = streamsets_api_client.api_client.get_pipeline(pipeline_.name)
        new_config = get_sdc_creator(pipeline_)\
            .override_base_config(new_uuid=api_pipeline['uuid'], new_title=pipeline_.name)
        streamsets_api_client.api_client.update_pipeline(pipeline_.name, new_config)
    except (config_handlers.base.ConfigHandlerException, streamsets_api_client.StreamSetsApiClientException) as e:
        raise pipeline.PipelineException(str(e))
    pipeline.repository.save(pipeline_)
    if start_pipeline:
        start(pipeline_)


def update_source_pipelines(source_: source.Source):
    for pipeline_ in pipeline.repository.get_by_source(source_.name):
        try:
            update(pipeline_)
        except pipeline.PipelineException as e:
            print(str(e))
            continue
        print(f'Pipeline {pipeline_.name} updated')


def get_pipeline_status(pipeline_id: str) -> str:
    return streamsets_api_client.api_client.get_pipeline_status(pipeline_id)['status']


def check_status(pipeline_id: str, status: str) -> bool:
    return get_pipeline_status(pipeline_id) == status


def wait_for_status(pipeline_id: str, status: str, tries: int = 5, initial_delay: int = 3):
    for i in range(1, tries + 1):
        response = streamsets_api_client.api_client.get_pipeline_status(pipeline_id)
        if response['status'] == status:
            return True
        delay = initial_delay ** i
        if i == tries:
            raise PipelineFreezeException(f"Pipeline {pipeline_id} is still {response['status']} after {tries} tries")
        print(f"Pipeline {pipeline_id} is {response['status']}. Check again after {delay} seconds...")
        time.sleep(delay)


def wait_for_sending_data(pipeline_id: str, tries: int = 5, initial_delay: int = 2):
    for i in range(1, tries + 1):
        response = streamsets_api_client.api_client.get_pipeline_metrics(pipeline_id)
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
        streamsets_api_client.api_client.stop_pipeline(pipeline_id)
    except streamsets_api_client.StreamSetsApiClientException:
        pass

    if not check_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPING):
        raise pipeline.PipelineException("Can't force stop a pipeline not in the STOPPING state")

    streamsets_api_client.api_client.force_stop_pipeline(pipeline_id)
    wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)


def stop(pipeline_: Pipeline):
    return stop_by_id(pipeline_.name)


def stop_by_id(pipeline_id: str):
    print("Stopping the pipeline")
    streamsets_api_client.api_client.stop_pipeline(pipeline_id)
    try:
        wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)
    except PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop_pipeline(pipeline_id)


def reset(pipeline_: Pipeline):
    try:
        streamsets_api_client.api_client.reset_pipeline(pipeline_.name)
        get_sdc_creator(pipeline_).set_initial_offset()
    except (config_handlers.base.ConfigHandlerException, streamsets_api_client.StreamSetsApiClientException) as e:
        raise pipeline.PipelineException(str(e))


def _delete_schema(pipeline_: Pipeline):
    if 'schema' in pipeline_.config:
        anodot_api_client.AnodotApiClient(pipeline_.destination).delete_schema(pipeline_.config['schema']['id'])


def _delete_from_streamsets(pipeline_id: str):
    if check_status(pipeline_id, pipeline.Pipeline.STATUS_RUNNING):
        stop_by_id(pipeline_id)
    streamsets_api_client.api_client.delete_pipeline(pipeline_id)


def delete(pipeline_: Pipeline):
    _delete_schema(pipeline_)
    try:
        _delete_from_streamsets(pipeline_.name)
    except streamsets_api_client.StreamSetsApiClientException as e:
        raise pipeline.PipelineException(str(e))
    finally:
        pipeline.repository.delete(pipeline_)


def delete_by_name(pipeline_name: str):
    delete(pipeline.repository.get_by_name(pipeline_name))


def force_delete(pipeline_name: str) -> list:
    """
    Try do delete everything related to the pipeline
    :param pipeline_name: string
    :return: list of errors that occurred during deletion
    """
    exceptions = []
    try:
        _delete_from_streamsets(pipeline_name)
    except Exception as e:
        exceptions.append(str(e))
    if pipeline.repository.exists(pipeline_name):
        pipeline_ = pipeline.repository.get_by_name(pipeline_name)
        try:
            _delete_schema(pipeline_)
        except Exception as e:
            exceptions.append(str(e))
        pipeline.repository.delete(pipeline_)
    return exceptions


def enable_destination_logs(pipeline_: Pipeline):
    pipeline_.destination.enable_logs()
    destination.repository.save(pipeline_.destination)
    update(pipeline_)


def disable_destination_logs(pipeline_: Pipeline):
    pipeline_.destination.disable_logs()
    destination.repository.save(pipeline_.destination)
    update(pipeline_)


def _update_stage_config(source_: source.Source, stage):
    for conf in stage['configuration']:
        if conf['name'] in source_.config:
            conf['value'] = source_.config[conf['name']]


def build_test_pipeline(source_: source.Source):
    # test_source = source.Source(source_.name, source_.type, source_.config)
    return pipeline.Pipeline(_get_test_pipeline_name(source_), source_, destination.repository.get())


def create_test_pipeline(pipeline_: pipeline.Pipeline) -> str:
    with open(_get_test_pipeline_file_path(pipeline_.source_)) as f:
        pipeline_config_ = json.load(f)['pipelineConfig']

    test_pipeline_name = _get_test_pipeline_name(pipeline_.source_)

    new_pipeline = streamsets_api_client.api_client.create_pipeline(test_pipeline_name)
    pipeline_config = get_sdc_creator(pipeline_, is_preview=True) \
        .override_base_config(new_uuid=new_pipeline['uuid'], base_config=pipeline_config_)
    streamsets_api_client.api_client.update_pipeline(test_pipeline_name, pipeline_config)
    pipeline.repository.remove_from_session(pipeline_)
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
    pipeline_ = create_object(pipeline.MONITORING, MONITORING_SOURCE_NAME)
    create(pipeline_)
    start(pipeline_)


def update_monitoring_pipeline():
    update(pipeline.repository.get_by_name(pipeline.MONITORING))


class PipelineFreezeException(Exception):
    pass


def transform_for_bc(pipeline_: Pipeline) -> dict:
    data = {
        'pipeline_id': pipeline_.name,
        'created': int(pipeline_.created_at.timestamp()),
        'updated': int(pipeline_.last_edited.timestamp()),
        'status': pipeline_.status,
        'schemaId': pipeline_.get_schema_id(),
        'source': {
            'name': pipeline_.source.name,
            'type': pipeline_.source.type,
        },
        'scheduling': {
            'interval': int(pipeline_.config.get('interval', 0)),
            'delay': int(pipeline_.config.get('delay', 0)),
        },
        # 'progress': {
        #     'last_offset': pipeline_.offset,
        # },
        'schema': pipeline_.get_schema() if pipeline_.get_schema_id() else schema.build(pipeline_),
        'config': pipeline_.config,
    }
    data['config'].pop('interval', 0)
    data['config'].pop('delay', 0)
    return data
