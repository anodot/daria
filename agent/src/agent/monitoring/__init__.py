import anodot
import requests
import urllib.parse

from . import metrics, streamsets, sender
from agent.modules import constants, logger
from datetime import datetime
from agent import pipeline
from agent.pipeline import Pipeline
from typing import Dict

logger_ = logger.get_logger(__name__)


def pull_latest():
    streamsets.pull_metrics()


def get_monitoring_metrics() -> list[dict]:
    pull_latest()
    data = []
    pipelines = pipeline.repository.get_all()
    # pipelines: Dict[str, Pipeline] = dict(zip({p.name for p in pipelines}, pipelines))
    for metric in streamsets.get_metrics():
        for bean in metric['beans']:
            for key in bean.keys():
                target_type = anodot.TargetType.COUNTER if key.endswith('Count') else anodot.TargetType.GAUGE
                if 'MemoryUsage' in key:
                    bean[key] = bean[key]['used']
                if isinstance(bean[key], (str, list)):
                    continue

                data.append(
                    anodot.Metric20(key, bean[key], target_type, datetime.utcnow()).to_dict()
                )
    return data


def increase_scheduled_script_error_counter(script_name):
    url = f'{constants.AGENT_MONITORING_ENDPOINT}/scheduled_script_error/' + script_name
    requests.post(url).raise_for_status()


def set_scheduled_script_execution_time(script_name, duration):
    url = constants.AGENT_MONITORING_ENDPOINT + '/scheduled_script_execution_time/' + script_name
    requests.post(url, json={'duration': duration}).raise_for_status()


def set_watermark_delta(pipeline_id: str, delta):
    url = f'{constants.AGENT_MONITORING_ENDPOINT}/watermark_delta/{pipeline_id}'
    requests.post(url, params={'delta': delta}).raise_for_status()


def set_watermark_sent(pipeline_id: str):
    url = f'{constants.AGENT_MONITORING_ENDPOINT}/watermark_sent/{pipeline_id}'
    requests.post(url).raise_for_status()


def run():
    url = constants.AGENT_MONITORING_ENDPOINT
    requests.get(url).raise_for_status()


def get_monitoring_source_error_url(pipeline_: Pipeline) -> str:
    return urllib.parse.urljoin(
        pipeline_.streamsets.agent_external_url, f'/monitoring/source_http_error/{pipeline_.name}/'
    )
