import json
import logging
import click
import os
import time
import agent.pipeline.config.handlers as config_handlers
import jsonschema

from agent import source, pipeline, destination
from agent.pipeline.streamsets import StreamSetsApiClient, StreamSets
from agent.pipeline.config import schema
from agent.pipeline.config.validators import get_config_validator
from agent.pipeline import prompt, load_client_data, Pipeline
from agent.destination import anodot_api_client
from agent.pipeline import streamsets
from agent.modules.constants import ENV_PROD, MONITORING_SOURCE_NAME
from agent.modules.tools import print_json, sdc_record_map_to_dict
from agent.modules.logger import get_logger
from typing import List

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
        preview = streamsets.manager.create_preview(pipeline_.name)
        preview_data, errors = streamsets.manager.wait_for_preview(pipeline_.name, preview['previewerId'])
    except streamsets.StreamSetsApiClientException as e:
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


def create_object(pipeline_id: str, source_name: str, streamsets_: StreamSets = None) -> Pipeline:
    pipeline_ = pipeline.Pipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get(),
        streamsets_ if streamsets_ else pipeline.streamsets.manager.choose_streamsets(),
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
    streamsets.manager.start(pipeline_.name)
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
        streamsets_pipeline = streamsets.manager.create_pipeline(pipeline_.name)
        new_config = get_sdc_creator(pipeline_)\
            .override_base_config(new_uuid=streamsets_pipeline['uuid'], new_title=pipeline_.name)
        streamsets.manager.update_pipeline(pipeline_.name, new_config)
    except (config_handlers.base.ConfigHandlerException, streamsets.StreamSetsApiClientException) as e:
        try:
            streamsets.manager.delete(pipeline_.name)
        except streamsets.StreamSetsApiClientException:
            # ignore if it doesn't exist in streamsets
            pass
        raise pipeline.PipelineException(str(e))


def update(pipeline_: Pipeline):
    start_pipeline = False
    try:
        if streamsets.manager.get_pipeline_status(pipeline_.name) in [pipeline.Pipeline.STATUS_RUNNING, pipeline.Pipeline.STATUS_RETRY]:
            streamsets.manager.stop(pipeline_.name)
            start_pipeline = True
        api_pipeline = streamsets.manager.get_pipeline(pipeline_.name)
        new_config = get_sdc_creator(pipeline_)\
            .override_base_config(new_uuid=api_pipeline['uuid'], new_title=pipeline_.name)
        streamsets.manager.update_pipeline(pipeline_.name, new_config)
    except (config_handlers.base.ConfigHandlerException, streamsets.StreamSetsApiClientException) as e:
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


def wait_for_sending_data(pipeline_id: str, tries: int = 5, initial_delay: int = 2):
    for i in range(1, tries + 1):
        response = streamsets.manager.get_pipeline_metrics(pipeline_id)
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


def reset(pipeline_: Pipeline):
    try:
        streamsets.manager.reset_pipeline(pipeline_.name)
        get_sdc_creator(pipeline_).set_initial_offset()
    except (config_handlers.base.ConfigHandlerException, streamsets.StreamSetsApiClientException) as e:
        raise pipeline.PipelineException(str(e))


def _delete_schema(pipeline_: Pipeline):
    if 'schema' in pipeline_.config:
        anodot_api_client.AnodotApiClient(pipeline_.destination).delete_schema(pipeline_.config['schema']['id'])


def delete(pipeline_: Pipeline):
    _delete_schema(pipeline_)
    try:
        streamsets.manager.delete(pipeline_.name)
    except streamsets.StreamSetsApiClientException as e:
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
        streamsets.manager.delete(pipeline_name)
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
    test_source = source.Source(source_.name, source_.type, source_.config)
    return pipeline.Pipeline(_get_test_pipeline_name(source_), test_source, destination.repository.get())


def create_test_pipeline(pipeline_: pipeline.Pipeline, streamsets_api_client: StreamSetsApiClient) -> str:
    with open(_get_test_pipeline_file_path(pipeline_.source_)) as f:
        pipeline_config_ = json.load(f)['pipelineConfig']

    test_pipeline_name = _get_test_pipeline_name(pipeline_.source_)

    new_pipeline = streamsets_api_client.create_pipeline(test_pipeline_name)
    pipeline_config = get_sdc_creator(pipeline_, is_preview=True) \
        .override_base_config(new_uuid=new_pipeline['uuid'], base_config=pipeline_config_)
    streamsets_api_client.update_pipeline(test_pipeline_name, pipeline_config)
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


def create_monitoring_pipelines():
    if not source.repository.exists(MONITORING_SOURCE_NAME):
        source.repository.save(source.Source(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {}))
    for streamsets_ in streamsets.manager.get_streamsets_without_monitoring():
        pipeline_ = create_object(f'{pipeline.MONITORING}_{streamsets_.id}', MONITORING_SOURCE_NAME, streamsets_)
        create(pipeline_)
        start(pipeline_)


def update_monitoring_pipelines():
    for streamsets_ in streamsets.repository.get_all():
        update(pipeline.repository.get_by_name(f'{pipeline.MONITORING}_{streamsets_.id}'))


def delete_monitoring_pipelines():
    for streamsets_ in streamsets.repository.get_all():
        pipeline.streamsets.manager.stop(f'{pipeline.MONITORING}_{streamsets_.id}')
        pipeline.manager.delete_by_name(f'{pipeline.MONITORING}_{streamsets_.id}')


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
            'delay': pipeline_.config.get('delay', 0),
        },
        'progress': {
            'last_offset': pipeline_.offset.offset if pipeline_.offset else '',
        },
        'schema': pipeline_.get_schema() if pipeline_.get_schema_id() else schema.build(pipeline_),
        'config': pipeline_.config,
    }
    data['config'].pop('interval', 0)
    data['config'].pop('delay', 0)
    return data
