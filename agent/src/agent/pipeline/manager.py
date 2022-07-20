import logging
import random
import string
import sdc_client

from datetime import datetime, timedelta

from agent import source, pipeline, destination, streamsets
from agent.modules import tools, constants
from agent.pipeline import Pipeline, TestPipeline, PipelineMetric, PipelineRetries, RawPipeline, EventsPipeline, \
    TopologyPipeline
from agent.pipeline import extra_setup, json_builder, schema
from agent.modules.logger import get_logger
from agent.pipeline.config.handlers.factory import get_config_handler
from agent.source import Source
from agent.pipeline import notifications

logger_ = get_logger(__name__, stdout=True)

LOG_LEVELS = [logging.getLevelName(logging.INFO), logging.getLevelName(logging.ERROR)]
MAX_SAMPLE_RECORDS = 3


def supports_schema(pipeline_: Pipeline) -> bool:
    if isinstance(pipeline_, (TestPipeline, RawPipeline, EventsPipeline, TopologyPipeline)):
        return False
    supported = {
        source.TYPE_CACTI: False,
        source.TYPE_CLICKHOUSE: True,
        source.TYPE_DIRECTORY: True,
        source.TYPE_DATABRICKS: True,
        source.TYPE_ELASTIC: False,
        source.TYPE_HTTP: True,
        source.TYPE_INFLUX: True,
        source.TYPE_INFLUX_2: True,
        source.TYPE_KAFKA: True,
        source.TYPE_MONGO: False,
        source.TYPE_MSSQL: True,
        source.TYPE_MYSQL: True,
        source.TYPE_OBSERVIUM: False,
        source.TYPE_ORACLE: True,
        source.TYPE_POSTGRES: True,
        source.TYPE_PROMETHEUS: True,
        source.TYPE_PRTG: True,
        source.TYPE_RRD: False,
        source.TYPE_SAGE: True,
        source.TYPE_SNMP: False,
        source.TYPE_SPLUNK: False,
        source.TYPE_SOLARWINDS: False,
        source.TYPE_THANOS: True,
        source.TYPE_TOPOLOGY: False,
        source.TYPE_VICTORIA: True,
        source.TYPE_ZABBIX: False,
    }
    return supported[pipeline_.source.type]


def create_pipeline(pipeline_id: str, source_name: str) -> Pipeline:
    return Pipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get(),
    )


def create_raw_pipeline(pipeline_id: str, source_name: str) -> RawPipeline:
    return RawPipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
    )


def create_events_pipeline(pipeline_id: str, source_name: str) -> EventsPipeline:
    return EventsPipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get(),
    )


def create_topology_pipeline(pipeline_id: str, source_name: str) -> TopologyPipeline:
    return TopologyPipeline(
        pipeline_id,
        source.repository.get_by_name(source_name),
        destination.repository.get(),
    )


def check_pipeline_id(pipeline_id: str):
    if pipeline.repository.exists(pipeline_id):
        raise pipeline.PipelineException(f"Pipeline {pipeline_id} already exists")


def start(pipeline_: Pipeline, wait_for_sending_data: bool = False):
    reset_pipeline_retries(pipeline_)
    if is_running(pipeline_):
        raise pipeline.exception.PipelineAlreadyRunningException(f"Pipeline {pipeline_.name} already running")
    sdc_client.start(pipeline_, wait_for_sending_data)


def stop(pipeline_: Pipeline):
    try:
        sdc_client.stop(pipeline_)
        reset_pipeline_retries(pipeline_)
    except (sdc_client.ApiClientException, sdc_client.StreamsetsException) as e:
        raise pipeline.PipelineException(str(e)) from e


def get_info(pipeline_: Pipeline, lines: int) -> dict:
    try:
        return sdc_client.get_pipeline_info(pipeline_, lines)
    except (sdc_client.ApiClientException, sdc_client.StreamsetsException) as e:
        raise pipeline.PipelineException(str(e)) from e


def get_metrics(pipeline_: Pipeline) -> PipelineMetric:
    try:
        return PipelineMetric(sdc_client.get_pipeline_metrics(pipeline_))
    except (sdc_client.ApiClientException, sdc_client.StreamsetsException) as e:
        raise pipeline.PipelineException(str(e)) from e


def reset_pipeline_retries(pipeline_: Pipeline):
    if pipeline_.retries:
        pipeline_.retries.notification_sent = False
        pipeline_.retries.number_of_error_statuses = 0
        pipeline.repository.save(pipeline_.retries)


def reset_pipeline_notifications(pipeline_: Pipeline):
    if pipeline_.notifications and pipeline_.notifications.no_data_notification:
        pipeline_.notifications.no_data_notification.notification_sent = False
        pipeline.repository.save(pipeline_.notifications.no_data_notification)


def _delete_pipeline_retries(pipeline_: Pipeline):
    if pipeline_.retries:
        pipeline.repository.delete_pipeline_retries(pipeline_.retries)


def _load_config(pipeline_: Pipeline, config: dict, is_edit=False):
    config['uses_schema'] = json_builder.get_schema_chooser(pipeline_).choose(pipeline_, config, is_edit)
    json_builder.get(pipeline_, config, is_edit).build()
    # todo too many validations, 4 validations here
    pipeline.config.validators.get_config_validator(pipeline_).validate(pipeline_)


def update(pipeline_: Pipeline, config_: dict = None):
    with pipeline.repository.SessionManager(pipeline_):
        if config_:
            _load_config(pipeline_, config_, is_edit=True)
        if not pipeline_.config_changed():
            logger_.info(f'No need to update pipeline {pipeline_.name}')
            return
        extra_setup.do(pipeline_)
        if pipeline_.uses_schema():
            _update_schema(pipeline_)
        sdc_client.update(pipeline_)
        reset_pipeline_retries(pipeline_)
        logger_.info(f'Updated pipeline {pipeline_.name}')


def create(pipeline_: Pipeline, config_: dict = None):
    with pipeline.repository.SessionManager(pipeline_):
        if config_:
            _load_config(pipeline_, config_)
        extra_setup.do(pipeline_)
        if pipeline_.uses_schema():
            _update_schema(pipeline_)
        notifications.repository.create_notifications(pipeline_)
        sdc_client.create(pipeline_)


def update_source_pipelines(source_: Source):
    for pipeline_ in pipeline.repository.get_by_source(source_.name):
        try:
            sdc_client.update(pipeline_)
        except streamsets.manager.StreamsetsException as e:
            logger_.debug(str(e), exc_info=True)
            continue
        logger_.info(f'Pipeline {pipeline_.name} updated')


def update_pipeline_offset(pipeline_: Pipeline, timestamp: float):
    offset = sdc_client.get_pipeline_offset(pipeline_)
    if not offset:
        return
    if pipeline_.offset:
        pipeline_.offset.offset = offset
        pipeline_.offset.timestamp = timestamp
    else:
        pipeline_.offset = pipeline.PipelineOffset(pipeline_.id, offset, timestamp)
    pipeline.repository.save(pipeline_.offset)


def update_pipeline_watermark(pipeline_: Pipeline, timestamp: float):
    if pipeline_.watermark:
        pipeline_.watermark.timestamp = timestamp
    else:
        pipeline_.watermark = pipeline.PipelineWatermark(pipeline_.name, timestamp)
    pipeline.repository.save(pipeline_.watermark)


def reset(pipeline_: Pipeline):
    try:
        sdc_client.reset(pipeline_)
        if pipeline_.offset:
            pipeline.repository.delete_offset(pipeline_.offset)
            pipeline_.offset = None
    except sdc_client.ApiClientException as e:
        raise pipeline.PipelineException(str(e)) from e


def _delete_schema(pipeline_: Pipeline):
    if pipeline_.has_schema():
        schema.delete(pipeline_.get_schema_id())
        pipeline_.schema = {}


def _update_schema(pipeline_: Pipeline):
    new_schema = schema.build(pipeline_)
    if old_schema := pipeline_.get_schema():
        if not schema.equal(old_schema, new_schema):
            pipeline_.schema = schema.update(new_schema)
        return
    pipeline_.schema = schema.create(new_schema)


def delete(pipeline_: Pipeline):
    _delete_schema(pipeline_)
    try:
        sdc_client.delete(pipeline_)
    except sdc_client.ApiClientException as e:
        raise pipeline.PipelineException(str(e)) from e
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
        try:
            sdc_client.force_delete(pipeline_id)
            if schema_id := schema.search(pipeline_id):
                schema.delete(schema_id)
        except Exception as e:
            exceptions.append(str(e))
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
    return TestPipeline(_get_test_pipeline_id(test_source), test_source)


def _get_test_pipeline_id(source_: Source) -> str:
    return '_'.join([source_.type, source_.name, 'preview', _generate_random_string()])


def _generate_random_string(size: int = 6):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))


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
    return data


def should_send_error_notification(pipeline_: Pipeline) -> bool:
    return not constants.DISABLE_PIPELINE_ERROR_NOTIFICATIONS \
           and pipeline_.error_notification_enabled()


def should_send_retries_error_notification(pipeline_: Pipeline) -> bool:
    # number of error statuses = number of retries + 1
    return should_send_error_notification(pipeline_) \
           and bool(pipeline_.retries) \
           and pipeline_.retries.number_of_error_statuses - 1 >= constants.STREAMSETS_NOTIFY_AFTER_RETRY_ATTEMPTS \
           and not pipeline_.retries.notification_sent


def should_send_no_data_error_notification(pipeline_: Pipeline) -> bool:
    if pipeline_.notifications and pipeline_.notifications.no_data_notification and pipeline_.offset:
        no_data_notification_period = timedelta(
            minutes=pipeline_.notifications.no_data_notification.notification_period
        ) + timedelta(seconds=pipeline_.interval or 0)
        no_data_time = datetime.now() - datetime.fromtimestamp(pipeline_.offset.timestamp)
        return should_send_error_notification(pipeline_) \
               and not pipeline_.notifications.no_data_notification.notification_sent \
               and no_data_time >= no_data_notification_period \
               and (not pipeline_.dvp_config or no_data_time >= timedelta(days=1))
    return False


def get_sample_records(pipeline_: Pipeline) -> (list, list):
    try:
        sdc_client.create(pipeline_)
        preview_data, errors = get_preview_data(pipeline_)
    finally:
        sdc_client.delete(pipeline_)

    if not preview_data or errors:
        return preview_data, errors

    try:
        data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
    except (ValueError, TypeError, IndexError) as e:
        logger_.debug(str(e), exc_info=True)
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
        logger_.debug(str(e), exc_info=True)
        raise
    return preview_data, errors


def create_streamsets_pipeline_config(pipeline_: Pipeline) -> dict:
    return get_config_handler(pipeline_).override_base_config()


def increase_retry_counter(pipeline_: Pipeline):
    if not pipeline_.retries:
        pipeline_.retries = PipelineRetries(pipeline_)
    pipeline_.retries.number_of_error_statuses += 1
    pipeline.repository.save(pipeline_.retries)


def is_running(pipeline_: Pipeline) -> bool:
    return sdc_client.get_pipeline_status(pipeline_) in [Pipeline.STATUS_RUNNING, Pipeline.STATUS_RETRY]
