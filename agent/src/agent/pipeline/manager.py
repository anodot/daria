import json
import logging
import random
import string
import traceback
import jsonschema

from agent import source, pipeline, destination, streamsets
from agent.modules import tools
from agent.pipeline.config import schema
from agent.pipeline.config.validators import get_config_validator
from agent.pipeline import load_client_data, Pipeline, TestPipeline
from agent.destination import anodot_api_client
from agent.modules.constants import MONITORING_SOURCE_NAME
from agent.modules.tools import print_json, sdc_record_map_to_dict
from agent.modules.logger import get_logger
from typing import List
from agent.source import Source
from agent.streamsets import StreamSets


logger = get_logger(__name__)

LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.ERROR)]
MAX_SAMPLE_RECORDS = 3


class PipelineBuilder:
    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.file_loader = get_file_loader(pipeline_.source.type)()

    def load_config(self, config, edit=False):
        self.pipeline.set_config(self.file_loader.load(config, edit))
        self._validate_config()

    def _validate_config(self):
        get_config_validator(self.pipeline).validate(self.pipeline)


def show_preview(pipeline_: Pipeline):
    try:
        preview = streamsets.manager.create_preview(pipeline_)
        preview_data, errors = streamsets.manager.wait_for_preview(pipeline_, preview['previewerId'])
    except streamsets.ApiClientException as e:
        print(str(e))
        return

    if preview_data['batchesOutput']:
        for output in preview_data['batchesOutput'][0]:
            if 'destination_OutputLane' in output['output']:
                data = output['output']['destination_OutputLane'][:MAX_SAMPLE_RECORDS]
                if data:
                    print_json([sdc_record_map_to_dict(record['value']) for record in data])
                else:
                    print('Could not fetch any data matching the provided config')
                break
    else:
        print('Could not fetch any data matching the provided config')
    print(*errors, sep='\n')


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
        destination.repository.get(),
    )
    return pipeline_


def check_pipeline_id(pipeline_id: str):
    if pipeline.repository.exists(pipeline_id):
        raise pipeline.PipelineException(f"Pipeline {pipeline_id} already exists")


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
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {traceback.format_exc()}'
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
    streamsets.manager.update(pipeline_builder.pipeline)
    pipeline.repository.save(pipeline_builder.pipeline)
    return pipeline_builder.pipeline


def create(pipeline_: Pipeline):
    streamsets.manager.create(pipeline_)
    pipeline.repository.save(pipeline_)


def update_source_pipelines(source_: Source):
    for pipeline_ in pipeline.repository.get_by_source(source_.name):
        try:
            streamsets.manager.update(pipeline_)
        except streamsets.manager.StreamsetsException as e:
            print(str(e))
            continue
        print(f'Pipeline {pipeline_.name} updated')


def update_pipeline_offset(pipeline_: Pipeline):
    offset = streamsets.manager.get_pipeline_offset(pipeline_)
    if not offset:
        return
    if pipeline_.offset:
        pipeline_.offset.offset = offset
    else:
        pipeline_.offset = pipeline.PipelineOffset(pipeline_.id, offset)
    pipeline.repository.save_offset(pipeline_.offset)


def reset(pipeline_: Pipeline):
    try:
        streamsets.manager.reset_pipeline(pipeline_)
        if pipeline_.offset:
            pipeline.repository.delete_offset(pipeline_.offset)
            pipeline_.offset = None
    except (streamsets.config_handlers.base.ConfigHandlerException, streamsets.ApiClientException) as e:
        raise pipeline.PipelineException(str(e))


def _delete_schema(pipeline_: Pipeline):
    if 'schema' in pipeline_.config:
        anodot_api_client.AnodotApiClient(pipeline_.destination).delete_schema(pipeline_.config['schema']['id'])


def delete(pipeline_: Pipeline):
    _delete_schema(pipeline_)
    try:
        streamsets.manager.delete(pipeline_)
    except streamsets.ApiClientException as e:
        raise pipeline.PipelineException(str(e))
    pipeline.repository.delete(pipeline_)
    pipeline.repository.add_deleted_pipeline_id(pipeline_.name)


def delete_by_name(pipeline_name: str):
    delete(pipeline.repository.get_by_name(pipeline_name))


def force_delete(pipeline_name: str) -> list:
    """
    Try do delete everything related to the pipeline
    :param pipeline_name: string
    :return: list of errors that occurred during deletion
    """
    exceptions = []
    pipeline_ = pipeline.repository.get_by_name(pipeline_name)
    try:
        streamsets.manager.delete(pipeline_)
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
    streamsets.manager.update(pipeline_)


def disable_destination_logs(pipeline_: Pipeline):
    pipeline_.destination.disable_logs()
    destination.repository.save(pipeline_.destination)
    streamsets.manager.update(pipeline_)


def build_test_pipeline(source_: Source) -> TestPipeline:
    # creating a new source because otherwise it will mess with the db session
    test_source = Source(source_.name, source_.type, source_.config)
    return TestPipeline(_get_test_pipeline_name(test_source), test_source, destination.repository.get())


def _get_test_pipeline_name(source_: Source) -> str:
    return '_'.join([source_.type, source_.name, 'preview', _generate_random_string()])


def _generate_random_string(size: int = 6):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))


def create_monitoring_pipelines():
    if not source.repository.exists(MONITORING_SOURCE_NAME):
        source.repository.save(Source(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {}))
    for streamsets_ in streamsets.manager.get_streamsets_without_monitoring():
        pipeline_ = create_object(get_monitoring_name(streamsets_), MONITORING_SOURCE_NAME)
        pipeline_.set_streamsets(streamsets_)
        streamsets.manager.create(pipeline_)
        pipeline.repository.save(pipeline_)
        streamsets.manager.start(pipeline_)


def update_monitoring_pipelines():
    for streamsets_ in streamsets.repository.get_all():
        streamsets.manager.update(
            pipeline.repository.get_by_name(get_monitoring_name(streamsets_))
        )


def delete_all_monitoring_pipelines():
    for streamsets_ in streamsets.repository.get_all():
        delete_monitoring_pipeline(streamsets_)


def delete_monitoring_pipeline(streamsets_: StreamSets):
    pipeline.manager.delete_by_name(get_monitoring_name(streamsets_))


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


def is_monitoring(pipeline_: Pipeline) -> bool:
    return pipeline_.name.startswith(pipeline.MONITORING)


def get_monitoring_name(streamsets_: StreamSets):
    return f'{pipeline.MONITORING}_{streamsets_.id}'


def get_sample_records(pipeline_: Pipeline) -> (list, list):
    preview_data, errors = _get_preview_data(pipeline_)

    if not preview_data:
        return [], []

    try:
        data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
    except (ValueError, TypeError, IndexError) as e:
        logger.exception(str(e))
        return [], []

    return [tools.sdc_record_map_to_dict(record['value']) for record in data[:MAX_SAMPLE_RECORDS]], errors


def _get_preview_data(test_pipeline: Pipeline):
    streamsets.manager.create(test_pipeline)
    try:
        preview = streamsets.manager.create_preview(test_pipeline)
        preview_data, errors = streamsets.manager.wait_for_preview(test_pipeline, preview['previewerId'])
    except (Exception, KeyboardInterrupt) as e:
        logger.exception(str(e))
        raise
    finally:
        streamsets.manager.delete(test_pipeline)
    return preview_data, errors
