import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from agent import pipeline
from agent.pipeline.streamsets import StreamSetsApiClient, StreamSets
from agent.pipeline import streamsets

_clients: Dict[int, StreamSetsApiClient] = {}


def _client(pipeline_id: str) -> StreamSetsApiClient:
    global _clients
    pipeline_ = pipeline.repository.get_by_name(pipeline_id)
    if pipeline_.streamsets.id not in _clients:
        _clients[pipeline_.streamsets.id] = StreamSetsApiClient(pipeline_.streamsets)
    return _clients[pipeline_.streamsets.id]


# todo return type
def get_pipeline(pipeline_id: str):
    return _client(pipeline_id).get_pipeline(pipeline_id)


def get_pipeline_logs(pipeline_id: str, severity: str, number_of_records: int) -> list:
    return _transform_logs(
        _client(pipeline_id).get_pipeline_logs(pipeline_id, severity)[:number_of_records]
    )


def _transform_logs(logs: dict) -> list:
    transformed = []
    for item in logs:
        if 'message' not in item:
            continue
        transformed.append([item['timestamp'], item['severity'], item['category'], item['message']])
    return transformed


def get_pipeline_status(pipeline_id: str) -> str:
    return _client(pipeline_id).get_pipeline_status(pipeline_id)['status']


def get_pipeline_metrics(pipeline_id: str):
    _client(pipeline_id).get_pipeline_metrics(pipeline_id)


def choose_streamsets() -> StreamSets:
    # choose streamsets with the lowest number of pipelines
    pipeline_streamsets = pipeline.repository.count_by_streamsets()
    streamsets_ = streamsets.repository.get_all()

    def foo(s: StreamSets):
        if s.id not in pipeline_streamsets:
            pipeline_streamsets[s.id] = 0

    map(foo, streamsets_)
    id_ = min(pipeline_streamsets, key=pipeline_streamsets.get)
    return streamsets.repository.get(id_)


def get_all_pipelines() -> List[dict]:
    pipelines = []
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        pipelines.append(client.get_pipelines())
    return pipelines


def get_all_pipeline_statuses() -> dict:
    # todo show streamsets id?
    statuses = {}
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        statuses = {**statuses, **client.get_pipeline_statuses()}
    return statuses


def get_streamsets_without_monitoring() -> List[StreamSets]:
    pipeline_streamsets_ids = set(map(
        lambda p: p.streamsets_id,
        pipeline.repository.get_all(),
    ))
    streamsets_ = streamsets.repository.get_all()
    streamsets_ids = set(map(
        lambda s: s.id,
        streamsets_,
    ))
    without_monitoring = streamsets_ids - pipeline_streamsets_ids
    return list(filter(
        lambda s: s.id in without_monitoring,
        streamsets_
    ))


def get_pipeline_info(pipeline_id: str, number_of_history_records: int) -> dict:
    client = _client(pipeline_id)
    status = client.get_pipeline_status(pipeline_id)
    metrics = json.loads(status['metrics']) if status['metrics'] else get_pipeline_metrics(pipeline_id)
    pipeline_info = client.get_pipeline(pipeline_id)
    history = client.get_pipeline_history(pipeline_id)
    info = {
        'status': '{status} {message}'.format(**status),
        'metrics': _get_metrics_string(metrics),
        'metric_errors': _get_metric_errors(pipeline_id, metrics),
        'pipeline_issues': _extract_pipeline_issues(pipeline_info),
        'stage_issues': _extract_stage_issues(pipeline_info),
        'history': _get_history_info(history, number_of_history_records)
    }
    return info


def _get_metrics_string(metrics_obj):
    if metrics_obj:
        stats = {
            'in': metrics_obj['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': metrics_obj['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': metrics_obj['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        stats['errors_perc'] = stats['errors'] * 100 / stats['in'] if stats['in'] != 0 else 0
        return 'In: {in} - Out: {out} - Errors {errors} ({errors_perc:.1f}%)'.format(**stats)
    return ''


def _get_metric_errors(pipeline_id: str, metrics: Optional[dict]) -> list:
    errors = []
    if metrics:
        for name, counter in metrics['counters'].items():
            stage_name = re.search('stage\.(.+)\.errorRecords\.counter', name)
            if counter['count'] == 0 or not stage_name:
                continue
            for error in _client(pipeline_id).get_pipeline_errors(pipeline_id, stage_name.group(1)):
                errors.append(f'{_get_timestamp(error["header"]["errorTimestamp"])} - {error["header"]["errorMessage"]}')
    return errors


def _get_timestamp(utc_time):
    return datetime.utcfromtimestamp(utc_time / 1000).strftime('%Y-%m-%d %H:%M:%S')


def _extract_pipeline_issues(pipeline_info: dict) -> list:
    pipeline_issues = []
    if pipeline_info['issues']['issueCount'] > 0:
        for i in pipeline_info['issues']['pipelineIssues']:
            pipeline_issues.append('{severity} - {configGroup} - {configName} - {message}'.format(**i))
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


def _get_history_info(history: list, number_of_history_records: int):
    info = []
    for item in history[:number_of_history_records]:
        metrics_str = _get_metrics_string(json.loads(item['metrics'])) if item['metrics'] else ' '
        message = item['message'] if item['message'] else ' '
        info.append([_get_timestamp(item['timeStamp']), item['status'], message, metrics_str])
    return info


def force_stop_pipeline(pipeline_id: str):
    client = _client(pipeline_id)
    try:
        client.stop_pipeline(pipeline_id)
    except streamsets.StreamSetsApiClientException:
        pass
    if not get_pipeline_status(pipeline_id) == pipeline.Pipeline.STATUS_STOPPING:
        raise pipeline.PipelineException("Can't force stop a pipeline not in the STOPPING state")
    client.force_stop_pipeline(pipeline_id)
    client.wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)


def stop(pipeline_id: str):
    print("Stopping the pipeline")
    client = _client(pipeline_id)
    client.stop_pipeline(pipeline_id)
    try:
        client.wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_STOPPED)
    except streamsets.PipelineFreezeException:
        print("Force stopping the pipeline")
        force_stop_pipeline(pipeline_id)


def reset_pipeline(pipeline_id: str):
    _client(pipeline_id).reset_pipeline(pipeline_id)


def delete(pipeline_id: str):
    if get_pipeline_status(pipeline_id) == pipeline.Pipeline.STATUS_RUNNING:
        streamsets.manager.stop(pipeline_id)
    _client(pipeline_id).delete_pipeline(pipeline_id)


def create_preview(pipeline_id: str):
    return _client(pipeline_id).create_preview(pipeline_id)


def wait_for_preview(pipeline_id: str, preview_id: str):
    return _client(pipeline_id).wait_for_preview(pipeline_id, preview_id)


def start(pipeline_id: str):
    client = _client(pipeline_id)
    client.start_pipeline(pipeline_id)
    client.wait_for_status(pipeline_id, pipeline.Pipeline.STATUS_RUNNING)


def create_pipeline(pipeline_id: str):
    return _client(pipeline_id).create_pipeline(pipeline_id)


def update_pipeline(pipeline_id: str, config: dict):
    return _client(pipeline_id).update_pipeline(pipeline_id, config)
