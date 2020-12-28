from agent import streamsets
from agent.monitoring import metrics


def get_streamsets_info():
    for client in streamsets.manager.get_clients().values():
        jmx = client.get_jmx()
        for bean in jmx['beans']:
            if bean['name'] == 'java.lang:type=Memory':
                metrics.STREAMSETS_HEAP_MEMORY.set(bean['HeapMemoryUsage']['used'])
                metrics.STREAMSETS_NON_HEAP_MEMORY.set(bean['NonHeapMemoryUsage']['used'])
            if bean['name'] == 'java.lang:type=OperatingSystem':
                metrics.STREAMSETS_CPU.set(bean['ProcessCpuLoad'])
