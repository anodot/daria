from prometheus_client import Info, Gauge, Summary, Enum
from agent import version
from agent.pipeline import Pipeline


VERSION = Info('version', 'Agent version')
VERSION.info({'version': version.__version__, 'build_time': version.__build_time__, 'git_sha1': version.__git_sha1__})

STREAMSETS_CPU = Gauge('streamsets_cpu', 'Streamsets CPU utilization')
STREAMSETS_HEAP_MEMORY = Gauge('streamsets_heap_mem', 'Streamsets Heap memory utilization')
STREAMSETS_NON_HEAP_MEMORY = Gauge('streamsets_non_heap_mem', 'Streamsets Non-heap memory utilization')

PIPELINE_INCOMING_RECORDS = Summary('pipeline_incoming_records', 'Pipeline incoming records')
PIPELINE_OUTGOING_RECORDS = Summary('pipeline_outgoing_records', 'Pipeline outgoing records')
PIPELINE_ERROR_RECORDS = Summary('pipeline_error_records', 'Pipeline error records')
PIPELINE_DESTINATION_LATENCY = Gauge('pipeline_destination_latency', 'Pipeline destination latency')

PIPELINE_STATUS = Enum('pipeline_status', 'Pipeline status', states=Pipeline.statuses)
PIPELINE_DELAY = Gauge('pipeline_delay_seconds', 'The difference between the latest saved offset and the current time')

AGENT_API_REQUESTS_TIME = Gauge('agent_api_requests_time_seconds', 'Agent API requests time in seconds')
# Do we need it?
AGENT_API_HEALTH_CHECK = Gauge('agent_api_health_check', 'Agent API health check')

AGENT_DB_REQUESTS_TIME = Gauge('agent_db_requests_time_seconds', 'Agent DB requests time in seconds')
# Do we need it?
AGENT_DB_HEALTH_CHECK = Gauge('agent_db_health_check', 'Agent DB health check')

KAFKA_CONSUMER_LAG = Gauge('kafka_consumer_lag', 'Kafka consumer lag')

# is there a better way to count them?
VICTORIA_HTTP_ERRORS = Summary('victoria_http_errors', 'VictoriaMetrics HTTP errors')
SAGE_HTTP_ERRORS = Summary('sage_http_errors', 'Sage HTTP errors')

# Or is it better to create a separate metric for each script?
SCHEDULED_SCRIPTS_ERRORS = Summary('scheduled_scripts_errors', 'Scheduled scripts errors')
