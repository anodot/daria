import logging
import random
import string
import sdc_client

from agent import source, pipeline, destination, streamsets
from agent.modules import tools, constants
from agent.pipeline import Pipeline, TestPipeline, schema, extra_setup, PipelineRetries
from agent.modules.logger import get_logger
from agent.pipeline.config.handlers.factory import get_config_handler
from agent.source import Source


logger_ = get_logger(__name__, stdout=True)

LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.ERROR)]
MAX_SAMPLE_RECORDS = 3


def supports_schema(pipeline_: Pipeline):
    supported = [
        source.TYPE_CLICKHOUSE,
        source.TYPE_DIRECTORY,
        source.TYPE_INFLUX,
        source.TYPE_KAFKA,
        source.TYPE_MYSQL,
        source.TYPE_POSTGRES,
    ]
    return pipeline_.source.type in supported


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    pipeline_ = Pipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get(),
    )
    return pipeline_


def check_pipeline_id(pipeline_id: str):
    if pipeline.repository.exists(pipeline_id):
        raise pipeline.PipelineException(f"Pipeline {pipeline_id} already exists")


def start(pipeline_: Pipeline):
    # remove saved retry attempts on pipeline start
    _reset_pipeline_retries(pipeline_)
    sdc_client.start(pipeline_)


def _reset_pipeline_retries(pipeline_: Pipeline):
    retries = pipeline.repository.get_pipeline_retries(pipeline_)
    if retries:
        retries.number_of_error_statuses = 0
        pipeline.repository.save_pipeline_retries(retries)


def _delete_pipeline_retries(pipeline_: Pipeline):
    retries = pipeline.repository.get_pipeline_retries(pipeline_)
    if retries:
        pipeline.repository.delete_pipeline_retries(retries)


def update(pipeline_: Pipeline):
    if not pipeline_.config_changed():
        logger_.info(f'No need to update pipeline {pipeline_.name}')
        return
    extra_setup.do(pipeline_)
    if pipeline_.uses_schema:
        _update_schema(pipeline_)
    sdc_client.update(pipeline_)
    pipeline.repository.save(pipeline_)
    logger_.info(f'Updated pipeline {pipeline_.name}')


def create(pipeline_: Pipeline):
    extra_setup.do(pipeline_)
    if pipeline_.uses_schema:
        _update_schema(pipeline_)
    sdc_client.create(pipeline_)
    pipeline.repository.save(pipeline_)


def update_source_pipelines(source_: Source):
    for pipeline_ in pipeline.repository.get_by_source(source_.name):
        try:
            sdc_client.update(pipeline_)
        except streamsets.manager.StreamsetsException as e:
            logger_.exception(str(e))
            continue
        logger_.info(f'Pipeline {pipeline_.name} updated')


def update_pipeline_offset(pipeline_: Pipeline):
    offset = sdc_client.get_pipeline_offset(pipeline_)
    if not offset:
        return
    if pipeline_.offset:
        pipeline_.offset.offset = offset
    else:
        pipeline_.offset = pipeline.PipelineOffset(pipeline_.id, offset)
    pipeline.repository.save_offset(pipeline_.offset)


def reset(pipeline_: Pipeline):
    try:
        sdc_client.reset(pipeline_)
        if pipeline_.offset:
            pipeline.repository.delete_offset(pipeline_.offset)
            pipeline_.offset = None
    except sdc_client.ApiClientException as e:
        raise pipeline.PipelineException(str(e))


def _delete_schema(pipeline_: Pipeline):
    if pipeline_.has_schema():
        schema.delete(pipeline_.get_schema_id())
        pipeline_.schema = {}


def _update_schema(pipeline_: Pipeline):
    new_schema = schema.build(pipeline_)
    old_schema = pipeline_.get_schema()
    if old_schema:
        if schema.equal(old_schema, new_schema):
            return
        schema.delete(pipeline_.get_schema_id())
    pipeline_.schema = schema.create(new_schema)


def delete(pipeline_: Pipeline):
    _delete_pipeline_retries(pipeline_)
    _delete_schema(pipeline_)
    try:
        sdc_client.delete(pipeline_)
    except sdc_client.ApiClientException as e:
        raise pipeline.PipelineException(str(e))
    if pipeline_.offset:
        pipeline.repository.delete_offset(pipeline_.offset)
    pipeline.repository.delete(pipeline_)
    pipeline.repository.add_deleted_pipeline_id(pipeline_.name)


def delete_by_id(pipeline_id: str):
    delete(pipeline.repository.get_by_id(pipeline_id))


def force_delete(pipeline_id: str) -> list:
    """
    Try do delete everything related to the pipeline
    :param pipeline_id: string
    :return: list of errors that occurred during deletion
    """
    exceptions = []
    if pipeline.repository.exists(pipeline_id):
        pipeline_ = pipeline.repository.get_by_id(pipeline_id)
        _delete_pipeline_retries(pipeline_)
        try:
            _delete_schema(pipeline_)
        except Exception as e:
            exceptions.append(str(e))
        try:
            sdc_client.delete(pipeline_)
        except Exception as e:
            exceptions.append(str(e))
        pipeline.repository.delete(pipeline_)
    else:
        sdc_client.force_delete(pipeline_id)
        schema_id = schema.search(pipeline_id)
        if schema_id:
            schema.delete(schema_id)
    return exceptions


def enable_destination_logs(pipeline_: Pipeline):
    pipeline_.destination.enable_logs()
    destination.repository.save(pipeline_.destination)
    sdc_client.update(pipeline_)


def disable_destination_logs(pipeline_: Pipeline):
    pipeline_.destination.disable_logs()
    destination.repository.save(pipeline_.destination)
    sdc_client.update(pipeline_)


def build_test_pipeline(source_: Source) -> TestPipeline:
    # creating a new source because otherwise it will mess with the db session
    test_source = source.manager.create_source_obj(source_.name, source_.type, source_.config)
    test_pipeline = TestPipeline(_get_test_pipeline_id(test_source), test_source, destination.repository.get())
    test_pipeline.config['uses_schema'] = supports_schema(test_pipeline)
    return test_pipeline


def _get_test_pipeline_id(source_: Source) -> str:
    return '_'.join([source_.type, source_.name, 'preview', _generate_random_string()])


def _generate_random_string(size: int = 6):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))


def transform_for_bc(pipeline_: Pipeline) -> dict:
    GENERAL_PIPELINE_ERROR_CODE = 70
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
            'interval': pipeline_.interval,
            'delay': pipeline_.delay,
        },
        'progress': {
            'last_offset': pipeline_.offset.offset if pipeline_.offset else '',
        },
        # we need to always send schema even if the pipeline doesn't use it
        'schema': pipeline_.get_schema() if pipeline_.get_schema_id() else schema.build(pipeline_),
        'config': pipeline_.config,
    }
    data['config'].pop('interval', 0)
    data['config'].pop('delay', 0)
    if _should_send_error_notification(pipeline_):
        data['notification'] = {
            'code': GENERAL_PIPELINE_ERROR_CODE,
            'description': 'pipeline error',
        }
    return data


def _should_send_error_notification(pipeline_: Pipeline) -> bool:
    retries = pipeline.repository.get_pipeline_retries(pipeline_)
    # number of error statuses = number of retries + 1
    # also streamsets sends status update twice on the last retry that's why we need to subtract 2
    return retries and retries.number_of_error_statuses - 2 >= constants.STREAMSETS_MAX_RETRY_ATTEMPTS and pipeline_.error_notification_enabled()


def get_sample_records(pipeline_: Pipeline) -> (list, list):
    try:
        sdc_client.create(pipeline_)
        preview_data, errors = get_preview_data(pipeline_)
    finally:
        sdc_client.delete(pipeline_)

    if not preview_data:
        return preview_data, errors

    try:
        data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
    except (ValueError, TypeError, IndexError) as e:
        logger_.exception(str(e))
        return [], []

    return [tools.sdc_record_map_to_dict(record['value']) for record in data[:MAX_SAMPLE_RECORDS]], errors


def get_preview_data(pipeline_: Pipeline) -> (list, list):
    try:
        preview = sdc_client.create_preview(pipeline_)
        preview_data, errors = sdc_client.wait_for_preview(pipeline_, preview['previewerId'])
    except sdc_client.ApiClientException as e:
        logger_.error(str(e))
        return [], []
    except (Exception, KeyboardInterrupt) as e:
        logger_.exception(str(e))
        raise
    return preview_data, errors


def create_streamsets_pipeline_config(pipeline_: Pipeline) -> dict:
    return get_config_handler(pipeline_).override_base_config()


def increase_retry_counter(pipeline_: Pipeline):
    retries = pipeline.repository.get_pipeline_retries(pipeline_)
    if not retries:
        retries = PipelineRetries(pipeline_)
    retries.number_of_error_statuses += 1
    pipeline.repository.save_pipeline_retries(retries)
