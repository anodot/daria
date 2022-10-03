import anodot
import requests
import urllib.parse

from . import metrics, streamsets, sender
from agent.modules import constants, logger
from agent.monitoring.dataclasses import Counter
from datetime import datetime
from agent import pipeline
from agent.pipeline import Pipeline
from typing import Dict, List

logger_ = logger.get_logger(__name__)


def pull_latest():
    streamsets.pull_metrics()


def get_monitoring_metrics() -> List[Dict]:
    pull_latest()
    data = []
    pipelines = pipeline.repository.get_all()
    pipelines: Dict[str, Pipeline] = dict(zip({p.name for p in pipelines}, pipelines))
    for metric in metrics.collect_metrics():
        target_type = anodot.TargetType.COUNTER if metric.type == 'counter' else anodot.TargetType.GAUGE
        for sample in metric.samples:
            print(sample)
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


def generate_latest():
    def sample_line(line):
        if line.labels:
            labelstr = '{{{0}}}'.format(','.join(
                ['{0}="{1}"'.format(
                    k, v.replace('\\', r'\\').replace('\n', r'\n').replace('"', r'\"'))
                    for k, v in sorted(line.labels.items())]))
        else:
            labelstr = ''
        timestamp = ''
        if line.timestamp is not None:
            # Convert to milliseconds.
            timestamp = ' {0:d}'.format(int(float(line.timestamp) * 1000))
        return '{0}{1} {2}{3}\n'.format(
            line.name, labelstr, str(line.value), timestamp)

    pull_latest()
    output = []
    for metric in metrics.collect_metrics():
        try:
            mname = metric.name
            mtype = metric.type
            # Munging from OpenMetrics into Prometheus format.
            if mtype == 'counter':
                mname = mname + '_total'
            elif mtype == 'info':
                mname = mname + '_info'
                mtype = 'gauge'
            elif mtype == 'stateset':
                mtype = 'gauge'
            elif mtype == 'gaugehistogram':
                # A gauge histogram is really a gauge,
                # but this captures the structure better.
                mtype = 'histogram'
            elif mtype == 'unknown':
                mtype = 'untyped'

            output.append('# HELP {0} {1}\n'.format(
                mname, metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0} {1}\n'.format(mname, mtype))

            om_samples = {}
            for s in metric.samples:
                for suffix in ['_created', '_gsum', '_gcount']:
                    if s.name == metric.name + suffix:
                        # OpenMetrics specific sample, put in a gauge at the end.
                        om_samples.setdefault(suffix, []).append(sample_line(s))
                        break
                else:
                    output.append(sample_line(s))
        except Exception as exception:
            exception.args = (exception.args or ('',)) + (metric,)
            raise

        for suffix, lines in sorted(om_samples.items()):
            output.append('# HELP {0}{1} {2}\n'.format(metric.name, suffix,
                                                       metric.documentation.replace('\\', r'\\').replace('\n',
                                                                                                         r'\n')))
            output.append('# TYPE {0}{1} gauge\n'.format(metric.name, suffix))
            output.extend(lines)
    return ''.join(output).encode('utf-8')