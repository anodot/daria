import contextlib
import json
import re
import time
import inject

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict
from sdc_client import balancer
from sdc_client.api_client import _StreamSetsApiClient, ApiClientException, PipelineFreezeException
from sdc_client.interfaces import ILogger, IStreamSets, IStreamSetsProvider, IPipeline

_clients: Dict[int, _StreamSetsApiClient] = {}


# TODO: pass StreamSets instance as an argument
def _client(pipeline: IPipeline) -> _StreamSetsApiClient:
    if not pipeline.get_streamsets():
        raise StreamsetsException(f'Pipeline `{pipeline.get_id()}` does not belong to any StreamSets')
    if pipeline.get_streamsets().get_id() not in _clients:
        _clients[pipeline.get_streamsets().get_id()] = _StreamSetsApiClient(pipeline.get_streamsets())
    return _clients[pipeline.get_streamsets().get_id()]


class Severity(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'


# TODO use _client method ?
def _get_client(streamsets: IStreamSets) -> _StreamSetsApiClient:
    global _clients
    if streamsets.get_id() not in _clients:
        _clients[streamsets.get_id()] = _StreamSetsApiClient(streamsets)
    return _clients[streamsets.get_id()]


def _get_streamsets_for_pipeline(pipeline: IPipeline):
    streamsets_pipelines = balancer.get_streamsets_pipelines()

    streamsets_with_preferred_type = {streamsets_: streamsets_pipelines[streamsets_]
                                      for streamsets_ in streamsets_pipelines
                                      if streamsets_.get_preferred_type() == pipeline.source_type
    }
    streamsets_to_get = streamsets_with_preferred_type or streamsets_pipelines
    return balancer.least_loaded_streamsets(streamsets_to_get)


def create(pipeline: IPipeline):
    # todo remove this if check and make streamsets mandatory after that fix todos above
    if not pipeline.get_streamsets():
        pipeline.set_streamsets(_get_streamsets_for_pipeline(pipeline))
    try:
        _client(pipeline).create_pipeline(pipeline.get_id())
    except ApiClientException as e:
        raise StreamsetsException(str(e))
    try:
        _update_pipeline(pipeline, set_offset=True)
    except ApiClientException as e:
        delete(pipeline)
        raise StreamsetsException(str(e))
    except Exception:
        delete(pipeline)
        raise


def update(pipeline: IPipeline):
    start_pipeline = False
    try:
        if get_pipeline_status(pipeline) in [IPipeline.STATUS_RUNNING, IPipeline.STATUS_RETRY]:
            stop(pipeline)
            start_pipeline = True
        _update_pipeline(pipeline)
    except ApiClientException as e:
        raise StreamsetsException(str(e))
    if start_pipeline:
        start(pipeline)


def exists(pipeline_id: str) -> bool:
    for streamsets in inject.instance(IStreamSetsProvider).get_all():
        if _exists(pipeline_id, streamsets):
            return True
    return False


def _exists(pipeline_id: str, streamsets: IStreamSets) -> bool:
    for pipeline_config in _get_client(streamsets).get_pipelines():
        if pipeline_config['title'] == pipeline_id:
            return True
    return False


def get_pipeline_logs(pipeline: IPipeline, severity: Optional[Severity], number_of_records: int) -> list:
    client = _client(pipeline)
    if severity is not None:
        severity = severity.value
    return _transform_logs(
        client.get_pipeline_logs(pipeline.get_id(), severity)[:number_of_records]
    )


def get_pipeline_status(pipeline: IPipeline) -> str:
    return _client(pipeline).get_pipeline_status(pipeline.get_id())['status']


def get_pipeline_metrics(pipeline: IPipeline) -> dict:
    return _client(pipeline).get_pipeline_metrics(pipeline.get_id())


def get_all_pipelines() -> List[dict]:
    pipelines = []
    for streamsets in inject.instance(IStreamSetsProvider).get_all():
        client = _StreamSetsApiClient(streamsets)
        with contextlib.suppress(Exception):
            pipelines += client.get_pipelines()
    return pipelines


def get_pipeline_streamsets_stat(pipeline: IPipeline) -> dict:
    try:
        stat = _client(pipeline).system_stats()
    except Exception:
        stat = None
    return stat


def get_all_pipeline_statuses() -> dict:
    statuses = {}
    for streamsets in inject.instance(IStreamSetsProvider).get_all():
        client = _StreamSetsApiClient(streamsets)
        with contextlib.suppress(Exception):
            statuses = {**statuses, **client.get_pipeline_statuses()}
    return statuses


def get_pipeline_info(pipeline: IPipeline, number_of_history_records: int) -> dict:
    client = _client(pipeline)
    status = client.get_pipeline_status(pipeline.get_id())
    metrics = json.loads(status['metrics']) if status['metrics'] else get_pipeline_metrics(pipeline)
    pipeline_info = client.get_pipeline(pipeline.get_id())
    history = client.get_pipeline_history(pipeline.get_id())
    return {
        'status': '{status} {message}'.format(**status),
        'metrics': _get_metrics_string(metrics),
        'metric_errors': _get_metric_errors(pipeline, metrics),
        'pipeline_issues': _extract_pipeline_issues(pipeline_info),
        'stage_issues': _extract_stage_issues(pipeline_info),
        'history': _get_history_info(history, number_of_history_records)
    }


def _get_metrics_string(metrics_: dict) -> str:
    if metrics_:
        stats = {
            'in': metrics_['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': metrics_['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': metrics_['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        stats['errors_perc'] = stats['errors'] * 100 / stats['in'] if stats['in'] != 0 else 0
        return 'In: {in} - Out: {out} - Errors {errors} ({errors_perc:.1f}%)'.format(**stats)
    return ''


def _get_metric_errors(pipeline: IPipeline, metrics: Optional[dict]) -> list:
    errors = []
    if metrics:
        for name, counter in metrics['counters'].items():
            stage_name = re.search(r'stage\.(.+)\.errorRecords\.counter', name)
            if counter['count'] == 0 or not stage_name:
                continue
            for error in _client(pipeline).get_pipeline_errors(pipeline.get_id(), stage_name.group(1)):
                errors.append(
                    f'{_format_timestamp(error["header"]["errorTimestamp"])} - {error["header"]["errorMessage"]}')
    return errors


def _extract_pipeline_issues(pipeline_info: dict) -> list:
    pipeline_issues = []
    if pipeline_info['issues']['issueCount'] > 0:
        for issue in pipeline_info['issues']['pipelineIssues']:
            pipeline_issues.append(_format(issue))
    return pipeline_issues


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
        message = item['message'] or ' '
        info.append([_format_timestamp(item['timeStamp']), item['status'], message, metrics_str])
    return info


def force_stop(pipeline: IPipeline):
    client = _client(pipeline)
    try:
        # todo IT SHOULD FORCE STOP
        client.stop_pipeline(pipeline.get_id())
    except ApiClientException:
        pass
    status = get_pipeline_status(pipeline)
    if status == IPipeline.STATUS_STOPPED:
        return
    if status != IPipeline.STATUS_STOPPING:
        raise PipelineException("Can't force stop a pipeline not in the STOPPING state")
    client.force_stop(pipeline.get_id())
    client.wait_for_status(pipeline.get_id(), IPipeline.STATUS_STOPPED)


def stop(pipeline: IPipeline):
    inject.instance(ILogger).info(f'Stopping the pipeline `{pipeline.get_id()}`')
    client = _client(pipeline)
    client.stop_pipeline(pipeline.get_id())
    try:
        client.wait_for_status(pipeline.get_id(), IPipeline.STATUS_STOPPED)
    except PipelineFreezeException:
        inject.instance(ILogger).info(f'Force stopping the pipeline `{pipeline.get_id()}`')
        force_stop(pipeline)


def reset(pipeline: IPipeline):
    _client(pipeline).reset_pipeline(pipeline.get_id())


def delete(pipeline: IPipeline):
    if get_pipeline_status(pipeline) in [IPipeline.STATUS_RUNNING, IPipeline.STATUS_RETRY]:
        stop(pipeline)
    _client(pipeline).delete_pipeline(pipeline.get_id())
    pipeline.delete_streamsets()


def force_delete(pipeline_id: str):
    for streamsets in inject.instance(IStreamSetsProvider).get_all():
        if _exists(pipeline_id, streamsets):
            class AnonymousPipeline:
                def get_id(self):
                    return pipeline_id

                def get_streamsets(self):
                    return streamsets

                def delete_streamsets(self):
                    pass

            delete(AnonymousPipeline())


def create_preview(pipeline: IPipeline) -> dict:
    return _client(pipeline).create_preview(pipeline.get_id())


def wait_for_preview(pipeline: IPipeline, preview_id: str) -> (list, list):
    return _client(pipeline).wait_for_preview(pipeline.get_id(), preview_id)


def start(pipeline: IPipeline, wait_for_sending_data: bool = False):
    client = _client(pipeline)
    client.start_pipeline(pipeline.get_id())
    client.wait_for_status(pipeline.get_id(), IPipeline.STATUS_RUNNING)
    inject.instance(ILogger).info(f'{pipeline.get_id()} pipeline is running')
    if wait_for_sending_data:
        try:
            if _wait_for_sending_data(pipeline):
                inject.instance(ILogger).info(f'{pipeline.get_id()} pipeline is sending data')
            else:
                inject.instance(ILogger).info(f'{pipeline.get_id()} pipeline did not send any data')
        except PipelineException as e:
            inject.instance(ILogger).error(str(e))


def _update_pipeline(pipeline: IPipeline, set_offset=False):
    client = _client(pipeline)
    if set_offset and pipeline.get_offset():
        client.post_pipeline_offset(pipeline.get_id(), json.loads(pipeline.get_offset()))
    config = pipeline.get_streamsets_config()
    config['uuid'] = client.get_pipeline(pipeline.get_id())['uuid']
    return client.update_pipeline(pipeline.get_id(), config)


def _wait_for_sending_data(pipeline: IPipeline) -> bool:
    tries = 5
    initial_delay = 2
    for i in range(1, tries + 1):
        response = get_pipeline_metrics(pipeline)
        stats = {
            'in': response['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': response['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': response['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        if stats['out'] > 0 and stats['errors'] == 0:
            return True
        if stats['errors'] > 0:
            raise PipelineException(f"Pipeline {pipeline.get_id()} has {stats['errors']} errors")
        delay = initial_delay ** i
        if i == tries:
            inject.instance(ILogger).warning(
                f'Pipeline {pipeline.get_id()} did not send any data. Received number of records - {stats["in"]}')
            return False
        inject.instance(ILogger).info(
            f'Waiting for pipeline `{pipeline.get_id()}` to send data. Check again after {delay} seconds...')
        time.sleep(delay)


def validate(pipeline: IPipeline):
    return _client(pipeline).validate(pipeline.get_id())


def get_pipeline_offset(pipeline: IPipeline) -> Optional[str]:
    res = _client(pipeline).get_pipeline_offset(pipeline.get_id())
    if res:
        return json.dumps(res)
    return None


def get_jmx(streamsets: IStreamSets, query: str) -> dict:
    return _get_client(streamsets).get_jmx(query)


def _format_timestamp(utc_time) -> str:
    return datetime.utcfromtimestamp(utc_time / 1000).strftime('%Y-%m-%d %H:%M:%S')


def _format(info: dict) -> str:
    keys = ['severity', 'configGroup', 'configName', 'message']
    return ' - '.join(info[key] for key in keys if key in info)


def _transform_logs(logs: dict) -> list:
    return [
        [
            item['timestamp'],
            item['severity'],
            item['category'],
            item['message'],
        ]
        for item in logs
        if 'message' in item
    ]


def check_connection(streamsets: IStreamSets):
    _StreamSetsApiClient(streamsets).get_pipelines()


class PipelineException(Exception):
    pass


class StreamsetsException(Exception):
    pass
