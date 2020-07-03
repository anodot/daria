import json
import re

from datetime import datetime
from typing import Optional
from returns.result import Result, Success, Failure
from agent.streamsets_api_client import api_client, StreamSetsApiClientException


def get_logs(pipeline_id: str, number_of_records: int, level: str) -> Result[list, str]:
    try:
        logs = api_client.get_pipeline_logs(pipeline_id, level=level)
    except StreamSetsApiClientException as e:
        return Failure(str(e))
    return Success(_transform_logs(logs[:number_of_records]))


def _transform_logs(logs: dict) -> list:
    transformed = []
    for item in logs:
        if 'message' not in item:
            continue
        transformed.append([item['timestamp'], item['level'], item['category'], item['message']])
    return transformed


def get(pipeline_id: str, number_of_history_records: int) -> Result[dict, str]:
    try:
        status = api_client.get_pipeline_status(pipeline_id)
        metrics = json.loads(status['metrics']) if status['metrics'] else api_client.get_pipeline_metrics(pipeline_id)
        pipeline_info = api_client.get_pipeline(pipeline_id)
        history = api_client.get_pipeline_history(pipeline_id)
        info = {
            'status': '{status} {message}'.format(**status),
            'metrics': _get_metrics_string(metrics),
            'metric_errors': _get_metric_errors(pipeline_id, metrics),
            'pipeline_issues': _extract_pipeline_issues(pipeline_info),
            'stage_issues': _extract_stage_issues(pipeline_info),
            'history': _get_history_info(history, number_of_history_records)
        }
    except StreamSetsApiClientException as e:
        return Failure(str(e))
    return Success(info)


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
            for error in api_client.get_pipeline_errors(pipeline_id, stage_name.group(1)):
                errors.append(f'{_get_timestamp(error["header"]["errorTimestamp"])} - {error["header"]["errorMessage"]}')
    return errors


def _get_timestamp(utc_time):
    return datetime.utcfromtimestamp(utc_time / 1000).strftime('%Y-%m-%d %H:%M:%S')


def _extract_pipeline_issues(pipeline_info: dict) -> list:
    pipeline_issues = []
    if pipeline_info['issues']['issueCount'] > 0:
        for i in pipeline_info['issues']['pipelineIssues']:
            pipeline_issues.append('{level} - {configGroup} - {configName} - {message}'.format(**i))
    return pipeline_issues


def _extract_stage_issues(pipeline_info: dict) -> dict:
    stage_issues = {}
    if pipeline_info['issues']['issueCount'] > 0:
        for stage, issues in pipeline_info['issues']['stageIssues'].items():
            if stage not in stage_issues:
                stage_issues[stage] = []
            for i in issues:
                stage_issues[stage].append('{level} - {configGroup} - {configName} - {message}'.format(**i))
    return stage_issues


def _get_history_info(history: list, number_of_history_records: int):
    info = []
    for item in history[:number_of_history_records]:
        metrics_str = _get_metrics_string(json.loads(item['metrics'])) if item['metrics'] else ' '
        message = item['message'] if item['message'] else ' '
        info.append([_get_timestamp(item['timeStamp']), item['status'], message, metrics_str])
    return info
