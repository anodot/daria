import json
import re
import time

from datetime import datetime
from typing import Dict, List, Optional
from agent import pipeline, streamsets, source
from agent.modules import db
from agent.modules.constants import ENV_PROD
from agent.modules.logger import get_logger
from agent.streamsets import StreamSetsApiClient, StreamSets
from agent.pipeline import Pipeline

logger = get_logger(__name__, stdout=True)

_clients: Dict[int, StreamSetsApiClient] = {}


def create_streamsets(streamsets_: StreamSets):
    streamsets.repository.save(streamsets_)


def delete_streamsets(streamsets_: StreamSets):
    if _has_pipelines(streamsets_):
        if not _can_move_pipelines():
            raise StreamsetsException(
                'Cannot move pipelines to a different streamsets as only one streamsets instance exists, cannot delete streamsets that has pipelines'
            )
        streamsets.manager.StreamsetsBalancer().unload_streamsets(streamsets_)
    streamsets.repository.delete(streamsets_)


def _has_pipelines(streamsets_: StreamSets) -> bool:
    return True if len(pipeline.repository.get_by_streamsets_id(streamsets_.id)) >= 1 else False


def _can_move_pipelines():
    return len(streamsets.repository.get_all()) > 1

# TODO: pass StreamSets instance as an argument
def _client(pipeline_: Pipeline) -> StreamSetsApiClient:
    global _clients
    if not pipeline_.streamsets:
        raise StreamsetsException(f'Pipeline with ID `{pipeline_.name}` does not exist in streamsets')
    if pipeline_.streamsets.id not in _clients:
        _clients[pipeline_.streamsets.id] = StreamSetsApiClient(pipeline_.streamsets)
    return _clients[pipeline_.streamsets.id]


def create(pipeline_: Pipeline):
    if not pipeline_.streamsets:
        pipeline_.set_streamsets(_choose_streamsets())
    try:
        streamsets_pipeline = _create_pipeline(pipeline_)
    except streamsets.ApiClientException as e:
        raise StreamsetsException(str(e))
    try:
        _update_pipeline(
            pipeline_,
            _create_streamsets_pipeline_config(streamsets_pipeline, pipeline_)
        )
    except (streamsets.config_handlers.base.ConfigHandlerException, streamsets.ApiClientException) as e:
        delete(pipeline_)
        raise StreamsetsException(str(e))


def update(pipeline_: Pipeline):
    start_pipeline = False
    try:
        if get_pipeline_status(pipeline_) in [Pipeline.STATUS_RUNNING, Pipeline.STATUS_RETRY]:
            stop(pipeline_.name)
            start_pipeline = True
        _update_pipeline(
            pipeline_,
            _create_streamsets_pipeline_config(get_pipeline(pipeline_.name), pipeline_)
        )
    except (streamsets.config_handlers.base.ConfigHandlerException, streamsets.ApiClientException) as e:
        raise StreamsetsException(str(e))
    if start_pipeline:
        start(pipeline_)


def _create_streamsets_pipeline_config(streamsets_pipeline: dict, pipeline_: Pipeline) -> dict:
    return get_sdc_config_handler(pipeline_).override_base_config(
        _get_config_loader(pipeline_).load_base_config(pipeline_),
        new_uuid=streamsets_pipeline['uuid'],
        new_title=pipeline_.name
    )


def _get_config_loader(pipeline_: Pipeline):
    return streamsets.config_handlers.base.TestPipelineBaseConfigLoader \
        if isinstance(pipeline_, pipeline.TestPipeline) \
        else streamsets.config_handlers.base.BaseConfigLoader


def get_pipeline(pipeline_id: str) -> dict:
    return _client(pipeline.repository.get_by_name(pipeline_id)).get_pipeline(pipeline_id)


def get_pipeline_logs(pipeline_id: str, severity: str, number_of_records: int) -> list:
    client = _client(pipeline.repository.get_by_name(pipeline_id))
    return _transform_logs(
        client.get_pipeline_logs(pipeline_id, severity)[:number_of_records]
    )


def _transform_logs(logs: dict) -> list:
    transformed = []
    for item in logs:
        if 'message' not in item:
            continue
        transformed.append([item['timestamp'], item['severity'], item['category'], item['message']])
    return transformed


def get_pipeline_status_by_id(pipeline_id: str) -> str:
    return get_pipeline_status(pipeline.repository.get_by_name(pipeline_id))


def get_pipeline_status(pipeline_: Pipeline) -> str:
    return _client(pipeline_).get_pipeline_status(pipeline_.name)['status']


def get_pipeline_metrics(pipeline_id: str) -> dict:
    return _client(pipeline.repository.get_by_name(pipeline_id)).get_pipeline_metrics(pipeline_id)


def _choose_streamsets(*, exclude: int = None) -> StreamSets:
    def add_empty(s: StreamSets):
        if s.id not in pipeline_streamsets:
            pipeline_streamsets[s.id] = 0
    # choose streamsets with the lowest number of pipelines
    pipeline_streamsets = streamsets.repository.count_pipelines_by_streamsets()
    logger.info(pipeline_streamsets)
    map(add_empty, streamsets.repository.get_all())
    if exclude:
        del pipeline_streamsets[exclude]
    id_ = min(pipeline_streamsets, key=pipeline_streamsets.get)
    return streamsets.repository.get(id_)


def get_all_pipelines() -> List[dict]:
    pipelines = []
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        pipelines = pipelines + client.get_pipelines()
    return pipelines


def get_all_pipeline_statuses() -> dict:
    statuses = {}
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        statuses = {**statuses, **client.get_pipeline_statuses()}
    return statuses


def get_pipeline_info(pipeline_id: str, number_of_history_records: int) -> dict:
    pipeline_ = pipeline.repository.get_by_name(pipeline_id)
    client = _client(pipeline_)
    status = client.get_pipeline_status(pipeline_id)
    metrics = json.loads(status['metrics']) if status['metrics'] else get_pipeline_metrics(pipeline_id)
    pipeline_info = client.get_pipeline(pipeline_id)
    history = client.get_pipeline_history(pipeline_id)
    info = {
        'status': '{status} {message}'.format(**status),
        'metrics': _get_metrics_string(metrics),
        'metric_errors': _get_metric_errors(pipeline_, metrics),
        'pipeline_issues': _extract_pipeline_issues(pipeline_info),
        'stage_issues': _extract_stage_issues(pipeline_info),
        'history': _get_history_info(history, number_of_history_records)
    }
    return info


def _get_metrics_string(metrics_obj) -> str:
    if metrics_obj:
        stats = {
            'in': metrics_obj['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': metrics_obj['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': metrics_obj['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        stats['errors_perc'] = stats['errors'] * 100 / stats['in'] if stats['in'] != 0 else 0
        return 'In: {in} - Out: {out} - Errors {errors} ({errors_perc:.1f}%)'.format(**stats)
    return ''


def _get_metric_errors(pipeline_: Pipeline, metrics: Optional[dict]) -> list:
    errors = []
    if metrics:
        for name, counter in metrics['counters'].items():
            stage_name = re.search('stage\.(.+)\.errorRecords\.counter', name)
            if counter['count'] == 0 or not stage_name:
                continue
            for error in _client(pipeline_).get_pipeline_errors(pipeline_.name, stage_name.group(1)):
                errors.append(
                    f'{_format_timestamp(error["header"]["errorTimestamp"])} - {error["header"]["errorMessage"]}')
    return errors


def _format_timestamp(utc_time) -> str:
    return datetime.utcfromtimestamp(utc_time / 1000).strftime('%Y-%m-%d %H:%M:%S')


def _extract_pipeline_issues(pipeline_info: dict) -> list:
    pipeline_issues = []
    if pipeline_info['issues']['issueCount'] > 0:
        for issue in pipeline_info['issues']['pipelineIssues']:
            pipeline_issues.append(_format(issue))
    return pipeline_issues


def _format(info: dict) -> str:
    keys = ['severity', 'configGroup', 'configName', 'message']
    return ' - '.join([info[key] for key in keys if key in info])


def _extract_stage_issues(pipeline_info: dict) -> dict:
    stage_issues = {}
    if pipeline_info['issues']['issueCount'] > 0:
        for stage, issues in pipeline_info['issues']['stageIssues'].items():
            if stage not in stage_issues:
                stage_issues[stage] = []
            for i in issues:
                stage_issues[stage].append('{severity} - {configGroup} - {configName} - {message}'.format(**i))
    return stage_issues


def _get_history_info(history: list, number_of_history_records: int) -> list:
    info = []
    for item in history[:number_of_history_records]:
        metrics_str = _get_metrics_string(json.loads(item['metrics'])) if item['metrics'] else ' '
        message = item['message'] if item['message'] else ' '
        info.append([_format_timestamp(item['timeStamp']), item['status'], message, metrics_str])
    return info


def force_stop(pipeline_id: str):
    client = _client(pipeline.repository.get_by_name(pipeline_id))
    try:
        client.stop_pipeline(pipeline_id)
    except streamsets.ApiClientException:
        pass
    if not get_pipeline_status_by_id(pipeline_id) == Pipeline.STATUS_STOPPING:
        raise streamsets.PipelineException("Can't force stop a pipeline not in the STOPPING state")
    client.force_stop(pipeline_id)
    client.wait_for_status(pipeline_id, Pipeline.STATUS_STOPPED)


def stop(pipeline_id: str):
    print("Stopping the pipeline")
    client = _client(pipeline.repository.get_by_name(pipeline_id))
    client.stop_pipeline(pipeline_id)
    try:
        client.wait_for_status(pipeline_id, Pipeline.STATUS_STOPPED)
    except streamsets.PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop(pipeline_id)


def reset_pipeline(pipeline_: Pipeline):
    _client(pipeline_).reset_pipeline(pipeline_.name)


def delete(pipeline_: Pipeline):
    if get_pipeline_status(pipeline_) in [Pipeline.STATUS_RUNNING, Pipeline.STATUS_RETRY]:
        stop(pipeline_.name)
    _client(pipeline_).delete_pipeline(pipeline_.name)
    pipeline_.delete_streamsets()


def create_preview(pipeline_: Pipeline):
    return _client(pipeline_).create_preview(pipeline_.name)


def wait_for_preview(pipeline_: Pipeline, preview_id: str):
    return _client(pipeline_).wait_for_preview(pipeline_.name, preview_id)


def start(pipeline_: Pipeline):
    client = _client(pipeline_)
    client.start_pipeline(pipeline_.name)
    client.wait_for_status(pipeline_.name, Pipeline.STATUS_RUNNING)
    logger.info(f'{pipeline_.name} pipeline is running')
    if ENV_PROD:
        try:
            if _wait_for_sending_data(pipeline_.name):
                logger.info(f'{pipeline_.name} pipeline is sending data')
            else:
                logger.info(f'{pipeline_.name} pipeline did not send any data')
        except streamsets.PipelineException as e:
            logger.error(str(e))


def _create_pipeline(pipeline_: Pipeline):
    return _client(pipeline_).create_pipeline(pipeline_.name)


def _update_pipeline(pipeline_: Pipeline, config: dict):
    if pipeline_.offset:
        _client(pipeline_).post_pipeline_offset(pipeline_.name, json.loads(pipeline_.offset.offset))
    return _client(pipeline_).update_pipeline(pipeline_.name, config)


def _wait_for_sending_data(pipeline_id: str, tries: int = 5, initial_delay: int = 2):
    for i in range(1, tries + 1):
        response = get_pipeline_metrics(pipeline_id)
        stats = {
            'in': response['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': response['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': response['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        if stats['out'] > 0 and stats['errors'] == 0:
            return True
        if stats['errors'] > 0:
            raise streamsets.PipelineException(f"Pipeline {pipeline_id} has {stats['errors']} errors")
        delay = initial_delay ** i
        if i == tries:
            logger.warning(f'Pipeline {pipeline_id} did not send any data. Received number of records - {stats["in"]}')
            return False
        print(f'Waiting for pipeline {pipeline_id} to send data. Check again after {delay} seconds...')
        time.sleep(delay)


def validate(pipeline_: Pipeline):
    return _client(pipeline_).validate(pipeline_.name)


def get_pipeline_offset(pipeline_: Pipeline) -> Optional[str]:
    res = _client(pipeline_).get_pipeline_offset(pipeline_.name)
    if res:
        return json.dumps(res)
    return None


# TODO use _client method ?
def get_client(streamsets_: StreamSets) -> StreamSetsApiClient:
    global _clients
    if streamsets_.id not in _clients:
        _clients[streamsets_.id] = StreamSetsApiClient(streamsets_)
    return _clients[streamsets_.id]


class StreamsetsBalancer:
    def __init__(self):
        self.streamsets_pipelines: Dict[int, List[Pipeline]] = self._get_streamsets_pipelines()

    def balance(self):
        while not self.is_balanced():
            self.move_from_streamsets(self._get_busiest_streamsets_id())

    def unload_streamsets(self, streamsets_: StreamSets):
        for pipeline_ in self.streamsets_pipelines[streamsets_.id]:
            self._move(pipeline_, _choose_streamsets(exclude=streamsets_.id))

    def move_from_streamsets(self, streamsets_id: int):
        pipeline_ = self.streamsets_pipelines[streamsets_id].pop()
        self._move(pipeline_, _choose_streamsets())
        self.streamsets_pipelines[pipeline_.streamsets_id].append(pipeline_)
        logger.info(f'Moved `{pipeline_.name}` to `{pipeline_.streamsets.url}`')

    @staticmethod
    def _move(pipeline_: Pipeline, to_streamsets: StreamSets):
        logger.info(f'Moving `{pipeline_.name}` from `{pipeline_.streamsets.url}` to `{to_streamsets.url}`')
        should_start = pipeline_.status in [Pipeline.STATUS_STARTING, Pipeline.STATUS_RUNNING]

        delete(pipeline_)
        pipeline_.set_streamsets(to_streamsets)
        create(pipeline_)
        pipeline.repository.save(pipeline_)
        db.session().commit()
        if should_start:
            start(pipeline_)

    @staticmethod
    def _get_streamsets_pipelines() -> dict:
        pipelines = pipeline.repository.get_all()
        sp = {}
        for pipeline_ in pipelines:
            if pipeline_.streamsets_id not in sp:
                sp[pipeline_.streamsets_id] = []
            sp[pipeline_.streamsets_id].append(pipeline_)
        for streamsets_ in streamsets.repository.get_all():
            if streamsets_.id not in sp:
                sp[streamsets_.id] = []
        return sp

    def is_balanced(self) -> bool:
        if len(self.streamsets_pipelines.keys()) < 2:
            return True
        # streamsets are balanced if the difference in num of their pipelines is 0 or 1
        lengths = [len(pipelines_) for pipelines_ in self.streamsets_pipelines.values()]
        return max(lengths) - min(lengths) < 2

    def _get_busiest_streamsets_id(self) -> int:
        key, _ = max(self.streamsets_pipelines.items(), key=lambda x: len(x))
        return key


def get_sdc_config_handler(pipeline_: Pipeline, is_preview=False) -> streamsets.config_handlers.base.BaseConfigHandler:
    handlers = {
        source.TYPE_INFLUX: streamsets.config_handlers.influx.InfluxConfigHandler,
        source.TYPE_MONGO: streamsets.config_handlers.mongo.MongoConfigHandler,
        source.TYPE_KAFKA: streamsets.config_handlers.kafka.KafkaConfigHandler,
        source.TYPE_MYSQL: streamsets.config_handlers.jdbc.JDBCConfigHandler,
        source.TYPE_POSTGRES: streamsets.config_handlers.jdbc.JDBCConfigHandler,
        source.TYPE_ELASTIC: streamsets.config_handlers.elastic.ElasticConfigHandler,
        source.TYPE_SPLUNK: streamsets.config_handlers.tcp.TCPConfigHandler,
        source.TYPE_DIRECTORY: streamsets.config_handlers.directory.DirectoryConfigHandler,
        source.TYPE_SAGE: streamsets.config_handlers.sage.SageConfigHandler,
        source.TYPE_VICTORIA: streamsets.config_handlers.victoria.VictoriaConfigHandler,
    }
    return handlers[pipeline_.source.type](pipeline_, is_preview)


class StreamsetsException(Exception):
    pass
