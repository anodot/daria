from agent import streamsets, pipeline
from agent.monitoring import metrics


def _get_system_metrics(streamsets_: streamsets.StreamSets):
    client = streamsets.manager.get_client(streamsets_)
    jmx = client.get_jmx('java.lang:type=*')
    for bean in jmx['beans']:
        if bean['name'] == 'java.lang:type=Memory':
            metrics.STREAMSETS_HEAP_MEMORY.labels(streamsets_.url).set(bean['HeapMemoryUsage']['used'])
            metrics.STREAMSETS_NON_HEAP_MEMORY.labels(streamsets_.url).set(bean['NonHeapMemoryUsage']['used'])
        elif bean['name'] == 'java.lang:type=OperatingSystem':
            metrics.STREAMSETS_CPU.labels(streamsets_.url).set(bean['ProcessCpuLoad'])


def _get_pipeline_metrics(pipeline_: pipeline.Pipeline):
    client = streamsets.manager.get_client(pipeline_.streamsets)
    jmx = client.get_jmx(f'metrics:name=sdc.pipeline.{pipeline_.name}.*')
    labels = (pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)
    for bean in jmx['beans']:
        # TODO: do not access private property
        if bean['name'].endswith('source.batchProcessing.timer'):
            metrics.PIPELINE_SOURCE_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
            metric = metrics.PIPELINE_INCOMING_RECORDS.labels(*labels)
            metric.inc(bean['Count'] - metric._value.get())
        elif bean['name'].endswith('destination.batchProcessing.timer'):
            metrics.PIPELINE_DESTINATION_LATENCY.labels(*labels).set(bean['Mean'] / 1000)
            metric = metrics.PIPELINE_OUTGOING_RECORDS.labels(*labels)
            metric.inc(bean['Count'] - metric._value.get())
        elif bean['name'].endswith('pipeline.batchErrorRecords.counter'):
            metric = metrics.PIPELINE_ERROR_RECORDS.labels(*labels)
            metric.inc(bean['Count'] - metric._value.get())


def _get_kafka_metrics(streamsets_: streamsets.StreamSets):
    client = streamsets.manager.get_client(streamsets_)
    jmx = client.get_jmx('kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*,topic=*,partition=*')
    for bean in jmx['beans']:
        name = dict(item.split('=') for item in bean['name'].split(','))
        metrics.KAFKA_CONSUMER_LAG.labels(name['topic']).set(bean['records-lag-avg'])


def get_metrics():
    for streamsets_ in streamsets.repository.get_all():
        _get_system_metrics(streamsets_)
        _get_kafka_metrics(streamsets_)
    for pipeline_ in pipeline.repository.get_all():
        _get_pipeline_metrics(pipeline_)