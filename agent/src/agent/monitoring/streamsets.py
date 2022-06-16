import urllib

import prometheus_client
import sdc_client
import re

from typing import List, Tuple, Dict
from agent import streamsets, pipeline, source
from agent.monitoring import metrics
from agent.modules import constants


def _pull_system_metrics(streamsets_: streamsets.StreamSets, jmx=None):
    jmx = jmx or sdc_client.get_jmx(streamsets_, 'java.lang:type=*')
    for bean in jmx['beans']:
        if bean['name'] == 'java.lang:type=Memory':
            metrics.STREAMSETS_HEAP_MEMORY.labels(streamsets_.url).set(bean['HeapMemoryUsage']['used'])
            metrics.STREAMSETS_NON_HEAP_MEMORY.labels(streamsets_.url).set(bean['NonHeapMemoryUsage']['used'])
        elif bean['name'] == 'java.lang:type=OperatingSystem':
            metrics.STREAMSETS_CPU.labels(streamsets_.url).set(bean['ProcessCpuLoad'])


def _increase_counter(total: int, metric: prometheus_client.Counter):
    # TODO: do not access private property
    val = total - metric._value.get()
    if val > 0:
        metric.inc(val)


def _is_influx(pipeline_: pipeline.Pipeline):
    return pipeline_.source.type == source.TYPE_INFLUX


def _pull_pipeline_metrics(pipeline_: pipeline.Pipeline, jmx=None):
    jmx = jmx or sdc_client.get_jmx(pipeline_.streamsets, f'metrics:name=sdc.pipeline.{pipeline_.name}.*')
    labels = (pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)
    for bean in jmx['beans']:
        if bean['name'].endswith('source.batchProcessing.timer'):
            metrics.PIPELINE_SOURCE_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
        elif bean['name'].endswith('source.outputRecords.counter') and not _is_influx(pipeline_):
            _increase_counter(bean['Count'], metrics.PIPELINE_INCOMING_RECORDS.labels(*labels))
        elif bean['name'].endswith('transform_records.outputRecords.counter') and _is_influx(pipeline_):
            _increase_counter(bean['Count'], metrics.PIPELINE_INCOMING_RECORDS.labels(*labels))
        elif bean['name'].endswith('destination.batchProcessing.timer'):
            metrics.PIPELINE_DESTINATION_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
        elif bean['name'].endswith('destination.outputRecords.counter'):
            _increase_counter(bean['Count'], metrics.PIPELINE_OUTGOING_RECORDS.labels(*labels))
        elif bean['name'].endswith('pipeline.batchErrorRecords.counter'):
            _increase_counter(bean['Count'], metrics.PIPELINE_ERROR_RECORDS.labels(*labels))

    if constants.MONITORING_COLLECT_ALL_STAGES_PROCESSING_TIME:
        for bean in jmx['beans']:
            m = re.match('.+\.stage\.(.+)\.batchProcessing\.timer$', bean['name'])
            if not m:
                continue
            metrics.PIPELINE_STAGE_BATCH_PROCESSING_TIME_AVG.labels(*labels, m.group(1)).set(bean['Mean'] / 1000)
            metrics.PIPELINE_STAGE_BATCH_PROCESSING_TIME_50th.labels(*labels, m.group(1)).set(
                bean['50thPercentile'] / 1000)
            metrics.PIPELINE_STAGE_BATCH_PROCESSING_TIME_999th.labels(*labels, m.group(1)).set(
                bean['999thPercentile'] / 1000)


def _pull_kafka_metrics(streamsets_: streamsets.StreamSets, jmx=None):
    jmx = jmx or sdc_client.get_jmx(
        streamsets_,
        'kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*,topic=*,partition=*'
    )
    for bean in jmx['beans']:
        name = dict(item.split('=') for item in bean['name'].split(','))
        metrics.KAFKA_CONSUMER_LAG.labels(name['topic']).set(bean['records-lag-avg'])


def pull_metrics():
    streamsets_ = streamsets.repository.get_all()
    _process_streamsets_metrics(
        streamsets_=streamsets_,
        asynchronous=len(streamsets_) >= 2
    )
    pipelines = pipeline.repository.get_all()
    _process_pipeline_metrics(
        pipelines=pipelines,
        asynchronous=len(pipelines) >= 2
    )


def _process_pipeline_metrics(pipelines: List[pipeline.Pipeline], asynchronous: bool = False) -> None:
    if not asynchronous:
        for pipeline_ in pipelines:
            _pull_pipeline_metrics(pipeline_)
    else:

        jmxes = sdc_client.get_jmxes_async([
            (pipeline_.streamsets, f'metrics:name=sdc.pipeline.{pipeline_.name}.*',)
            for pipeline_ in pipelines])
        for pipeline_, jmx in zip(pipelines, jmxes):
            _pull_pipeline_metrics(pipeline_, jmx)


def _process_streamsets_metrics(streamsets_: List[streamsets.StreamSets], asynchronous: bool = False) -> None:
    if not asynchronous:
        for streamset_ in streamsets_:
            _pull_system_metrics(streamset_)
            _pull_kafka_metrics(streamset_)
    else:
        sys_queries = [(streamset_, 'java.lang:type=*',) for streamset_ in streamsets_]
        kafka_queries = [
            (streamset_, 'kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*,topic=*,partition=*',)
            for streamset_ in streamsets_]
        jmxes = sdc_client.get_jmxes_async(sys_queries + kafka_queries)
        for index, streamset_ in enumerate(streamsets_):
            _pull_system_metrics(streamset_, jmxes[index])
            _pull_kafka_metrics(streamset_, jmxes[index + len(streamsets_)])
