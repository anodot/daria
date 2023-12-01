import anodot
import requests
import urllib.parse

from . import metrics, streamsets, sender
from agent.modules import constants, logger
from agent.monitoring.dataclasses import Counter, Metric
from datetime import datetime
from agent import pipeline
from agent.pipeline import Pipeline
from typing import Dict, List

logger_ = logger.get_logger(__name__)


def pull_latest():
    streamsets.pull_metrics()


def get_monitoring_metrics_for_anodot() -> List[Dict]:
    pull_latest()
    data = []
    pipelines = pipeline.repository.get_all()
    pipelines: Dict[str, Pipeline] = dict(zip({p.name for p in pipelines}, pipelines))
    for metric in metrics.collect_metrics():
        target_type = anodot.TargetType.COUNTER if metric.type == 'counter' else anodot.TargetType.GAUGE
        for sample in metric.samples:
            if sample.name.endswith('_created'):
                continue
            if 'pipeline_id' in sample.labels and sample.labels['pipeline_id'] not in pipelines:
                continue
            if sample.labels.get('streamsets_url') and\
                    pipelines.get(sample.labels.get('pipeline_id')) and\
                    sample.labels.get('streamsets_url') != pipelines[sample.labels['pipeline_id']].streamsets.url:
                continue
            dims = {**sample.labels, 'host_name': constants.HOSTNAME, 'source': 'agent_monitoring'}
            data.append(
                anodot.Metric20(sample.name, sample.value, target_type, datetime.utcnow(), dimensions=dims).to_dict()
            )
    return data


def increase_scheduled_script_error_counter(script_name):
    url = f'{constants.AGENT_MONITORING_ENDPOINT}/scheduled_script_error/' + script_name
    requests.post(url).raise_for_status()


def set_scheduled_script_execution_time(script_name, duration):
    url = constants.AGENT_MONITORING_ENDPOINT + '/scheduled_script_execution_time/' + script_name
    requests.post(url, json={'duration': duration}).raise_for_status()


def set_watermark_sent(pipeline_id: str, watermark: int):
    url = f'{constants.AGENT_MONITORING_ENDPOINT}/watermark_sent/{pipeline_id}'
    requests.post(url, json={'watermark': watermark}).raise_for_status()


def run():
    url = constants.AGENT_MONITORING_ENDPOINT
    requests.get(url).raise_for_status()


def get_monitoring_source_error_url(pipeline_: Pipeline) -> str:
    return urllib.parse.urljoin(
        pipeline_.streamsets.agent_external_url, f'/monitoring/source_http_error/{pipeline_.name}/'
    )
