from agent import streamsets, pipeline
from agent.monitoring import metrics


def _get_system_info(streamsets_: streamsets.StreamSets):
    client = streamsets.manager.get_client(streamsets_)
    jmx = client.get_jmx('java.lang:type=*')
    for bean in jmx['beans']:
        if bean['name'] == 'java.lang:type=Memory':
            metrics.STREAMSETS_HEAP_MEMORY.labels(streamsets_.url).set(bean['HeapMemoryUsage']['used'])
            metrics.STREAMSETS_NON_HEAP_MEMORY.labels(streamsets_.url).set(bean['NonHeapMemoryUsage']['used'])
        if bean['name'] == 'java.lang:type=OperatingSystem':
            metrics.STREAMSETS_CPU.labels(streamsets_.url).set(bean['ProcessCpuLoad'])


def _get_pipeline_info(pipeline_: pipeline.Pipeline):
    client = streamsets.manager.get_client(pipeline_.streamsets)
    jmx = client.get_jmx(f'metrics:name=sdc.pipeline.{pipeline_.name}.*')
    for bean in jmx['beans']:
        if bean['name'].endswith('source.outputRecords.counter'):
            metrics.PIPELINE_INCOMING_RECORDS.labels(pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)


def get_streamsets_info():
    for streamsets_ in streamsets.repository.get_all():
        _get_system_info(streamsets_)
    for pipeline_ in pipeline.repository.get_all():
        _get_pipeline_info(pipeline_)