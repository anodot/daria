from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config.stages import JSConvertMetrics20, AddProperties, Filtering, Destination, Source

logger = get_logger(__name__)


class TCPConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'tcp_server_http.json'

    stages = {
        'source': Source,
        'JavaScriptEvaluator_01': JSConvertMetrics20,
        'ExpressionEvaluator_02': AddProperties,
        'ExpressionEvaluator_03': Filtering,
        'destination': Destination
    }
