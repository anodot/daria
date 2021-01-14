import prometheus_client

from agent import streamsets, pipeline, source
from agent.monitoring import metrics


def _pull_system_metrics(streamsets_: streamsets.StreamSets):
    client = streamsets.manager.get_client(streamsets_)
    jmx = client.get_jmx('java.lang:type=*')
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


def _pull_pipeline_metrics(pipeline_: pipeline.Pipeline):
    client = streamsets.manager.get_client(pipeline_.streamsets)
    jmx = client.get_jmx(f'metrics:name=sdc.pipeline.{pipeline_.name}.*')
    labels = (pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)
    for bean in jmx['beans']:
        if bean['name'].endswith('source.batchProcessing.timer'):
            metrics.PIPELINE_SOURCE_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
        elif bean['name'].endswith('source.outputRecords.timer') and not _is_influx(pipeline_):
            _increase_counter(bean['Count'], metrics.PIPELINE_INCOMING_RECORDS.labels(*labels))
        elif bean['name'].endswith('transform_records.outputRecords.counter') and _is_influx(pipeline_):
            _increase_counter(bean['Count'], metrics.PIPELINE_INCOMING_RECORDS.labels(*labels))
        elif bean['name'].endswith('destination.batchProcessing.timer'):
            metrics.PIPELINE_DESTINATION_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
        elif bean['name'].endswith('destination.outputRecords.counter'):
            _increase_counter(bean['Count'], metrics.PIPELINE_OUTGOING_RECORDS.labels(*labels))
        elif bean['name'].endswith('pipeline.batchErrorRecords.counter'):
            _increase_counter(bean['Count'], metrics.PIPELINE_ERROR_RECORDS.labels(*labels))


def _pull_kafka_metrics(streamsets_: streamsets.StreamSets):
    client = streamsets.manager.get_client(streamsets_)
    jmx = client.get_jmx('kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*,topic=*,partition=*')
    for bean in jmx['beans']:
        name = dict(item.split('=') for item in bean['name'].split(','))
        metrics.KAFKA_CONSUMER_LAG.labels(name['topic']).set(bean['records-lag-avg'])


def pull_metrics():
    for streamsets_ in streamsets.repository.get_all():
        _pull_system_metrics(streamsets_)
        _pull_kafka_metrics(streamsets_)
    for pipeline_ in pipeline.repository.get_all():
        _pull_pipeline_metrics(pipeline_)