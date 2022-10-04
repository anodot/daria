from prometheus_client import (Info,
    Counter as PrometheusCounter,
    Gauge as PrometheusGauge,
    CollectorRegistry,
)
from agent import version
from agent.monitoring.dataclasses import Counter, Gauge

registry = CollectorRegistry()

VERSION = Info('version', 'Agent version', registry=registry)
VERSION.info({'version': version.__version__})

STREAMSETS_CPU = Gauge('streamsets_cpu', 'Streamsets CPU utilization', ['streamsets_url'], multiprocess_mode='max')
STREAMSETS_HEAP_MEMORY = Gauge(
    'streamsets_heap_memory_used_bytes',
    'Streamsets Heap memory utilization', ['streamsets_url'],
    multiprocess_mode='max'
)
STREAMSETS_NON_HEAP_MEMORY = Gauge(
    'streamsets_non_heap_memory_used_bytes',
    'Streamsets Non-heap memory utilization', ['streamsets_url'],
    multiprocess_mode='max'
)

PIPELINE_INCOMING_RECORDS = Counter(
    'pipeline_incoming_records', 'Pipeline incoming records', ['streamsets_url', 'pipeline_id', 'pipeline_type']
)
PIPELINE_OUTGOING_RECORDS = Counter(
    'pipeline_outgoing_records', 'Pipeline outgoing records', ['streamsets_url', 'pipeline_id', 'pipeline_type']
)
PIPELINE_ERROR_RECORDS = Counter(
    'pipeline_error_records', 'Pipeline error records', ['streamsets_url', 'pipeline_id', 'pipeline_type']
)
PIPELINE_AVG_LAG = PrometheusGauge(
    'pipeline_avg_lag_seconds',
    'Pipeline average lag metrics', ['streamsets_url', 'pipeline_id', 'pipeline_type'],
    multiprocess_mode='max'
)
PIPELINE_DESTINATION_LATENCY = Gauge(
    'pipeline_destination_latency_seconds',
    'Pipeline destination latency', ['streamsets_url', 'pipeline_id', 'pipeline_type'],
    multiprocess_mode='max'
)
PIPELINE_SOURCE_LATENCY = Gauge(
    'pipeline_source_latency_seconds',
    'Pipeline source latency', ['streamsets_url', 'pipeline_id', 'pipeline_type'],
    multiprocess_mode='max'
)
PIPELINE_STAGE_BATCH_PROCESSING_TIME_AVG = Gauge(
    'pipeline_stage_patch_processing_time_avg_seconds',
    'Pipeline stage batch processing time avg', ['streamsets_url', 'pipeline_id', 'pipeline_type', 'stage'],
    multiprocess_mode='max'
)

PIPELINE_STAGE_BATCH_PROCESSING_TIME_50th = Gauge(
    'pipeline_stage_patch_processing_time_50th_seconds',
    'Pipeline stage batch processing time 50th percentile', ['streamsets_url', 'pipeline_id', 'pipeline_type', 'stage'],
    multiprocess_mode='max'
)

PIPELINE_STAGE_BATCH_PROCESSING_TIME_999th = Gauge(
    'pipeline_stage_patch_processing_time_999th_seconds',
    'Pipeline stage batch processing time 999th percentile',
    ['streamsets_url', 'pipeline_id', 'pipeline_type', 'stage'],
    multiprocess_mode='max'
)

PIPELINE_STATUS = Counter(
    'pipeline_status',
    'Pipeline status',
    ['streamsets_url', 'pipeline_id', 'pipeline_type', 'status'],
)

KAFKA_CONSUMER_LAG = Gauge('kafka_consumer_lag', 'Kafka consumer lag', ['topic'], multiprocess_mode='max')

SOURCE_HTTP_ERRORS = PrometheusCounter('source_http_errors', 'Source HTTP errors', ['pipeline_id', 'pipeline_type', 'code'])
SOURCE_MYSQL_ERRORS = PrometheusCounter('source_mysql_errors', 'Source MySQL errors', ['pipeline_id'])
SCHEDULED_SCRIPTS_ERRORS = PrometheusCounter('scheduled_scripts_errors', 'Scheduled scripts errors', ['script_name'])
SCHEDULED_SCRIPT_EXECUTION_TIME = PrometheusGauge(
    'scheduled_script_execution_time', 'Time to execute a scheduled script', ['script_name'], multiprocess_mode='max'
)

DIRECTORY_FILE_PROCESSED = PrometheusCounter(
    'directory_file_processed', 'Finished processing one file', ['streamsets_url', 'pipeline_id']
)

WATERMARK_DELTA = PrometheusGauge(
    'watermark_delta',
    'Difference between time.now() and watermark timestamp', ['streamsets_url', 'pipeline_id', 'pipeline_type'],
    multiprocess_mode='max'
)

WATERMARK_SENT = PrometheusCounter(
    'watermark_sent', 'Number of sent watermarks', ['streamsets_url', 'pipeline_id', 'pipeline_type']
)


def collect_metrics():
    return [
        *registry.collect(),
        STREAMSETS_CPU, STREAMSETS_HEAP_MEMORY, STREAMSETS_NON_HEAP_MEMORY,
        PIPELINE_INCOMING_RECORDS, PIPELINE_OUTGOING_RECORDS, PIPELINE_ERROR_RECORDS,
        PIPELINE_DESTINATION_LATENCY, PIPELINE_SOURCE_LATENCY,
        PIPELINE_STAGE_BATCH_PROCESSING_TIME_AVG, PIPELINE_STAGE_BATCH_PROCESSING_TIME_50th,
        PIPELINE_STAGE_BATCH_PROCESSING_TIME_999th, PIPELINE_STATUS, KAFKA_CONSUMER_LAG,
    ]
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
