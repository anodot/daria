from prometheus_client import Info, Gauge, Enum, Counter, CollectorRegistry
from agent import version
from agent.pipeline import Pipeline

registry = CollectorRegistry()

VERSION = Info('version', 'Agent version', registry=registry)
VERSION.info({'version': version.__version__})

STREAMSETS_CPU = Gauge('streamsets_cpu', 'Streamsets CPU utilization', ['streamsets_url'], registry=registry)
STREAMSETS_HEAP_MEMORY = Gauge('streamsets_heap_memory_used_bytes', 'Streamsets Heap memory utilization',
                               ['streamsets_url'], registry=registry)
STREAMSETS_NON_HEAP_MEMORY = Gauge('streamsets_non_heap_memory_used_bytes', 'Streamsets Non-heap memory utilization',
                                   ['streamsets_url'], registry=registry)

PIPELINE_INCOMING_RECORDS = Counter('pipeline_incoming_records', 'Pipeline incoming records',
                                    ['streamsets_url', 'pipeline_id', 'pipeline_type'], registry=registry)
PIPELINE_OUTGOING_RECORDS = Counter('pipeline_outgoing_records', 'Pipeline outgoing records',
                                    ['streamsets_url', 'pipeline_id', 'pipeline_type'], registry=registry)
PIPELINE_ERROR_RECORDS = Counter('pipeline_error_records', 'Pipeline error records',
                                 ['streamsets_url', 'pipeline_id', 'pipeline_type'], registry=registry)
PIPELINE_DESTINATION_LATENCY = Gauge('pipeline_destination_latency_seconds', 'Pipeline destination latency',
                                     ['streamsets_url', 'pipeline_id', 'pipeline_type'], registry=registry)
PIPELINE_SOURCE_LATENCY = Gauge('pipeline_source_latency_seconds', 'Pipeline source latency',
                                ['streamsets_url', 'pipeline_id', 'pipeline_type'], registry=registry)

PIPELINE_STATUS = Enum('pipeline_status', 'Pipeline status', ['streamsets_url', 'pipeline_id', 'pipeline_type'],
                       states=Pipeline.statuses, registry=registry)

KAFKA_CONSUMER_LAG = Gauge('kafka_consumer_lag', 'Kafka consumer lag', ['topic'], registry=registry)

SOURCE_HTTP_ERRORS = Counter('source_http_errors', 'Source HTTP errors',
                             ['streamsets_url', 'pipeline_id', 'pipeline_type', 'code'], registry=registry)
SCHEDULED_SCRIPTS_ERRORS = Counter('scheduled_scripts_errors', 'Scheduled scripts errors', ['script_name'],
                                   registry=registry)

# # Not for every endpoint
# AGENT_API_REQUESTS_LATENCY = Gauge('agent_api_requests_latency_seconds', 'Agent API requests time in seconds',
#                                    ['endpoint'], registry=registry)
# # Do we need it?
# AGENT_API_HEALTH_CHECK = Gauge('agent_api_health_check', 'Agent API health check', registry=registry)
#
# AGENT_DB_REQUESTS_LATENCY = Gauge('agent_db_requests_latency_seconds', 'Agent DB requests time in seconds',
#                                   registry=registry)
# # Do we need it?
# AGENT_DB_HEALTH_CHECK = Gauge('agent_db_health_check', 'Agent DB health check', registry=registry)
