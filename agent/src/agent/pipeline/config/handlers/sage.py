from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config.stages import JSConvertMetrics, AddProperties, Destination, Sage

logger = get_logger(__name__)


class SageConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'sage_http.json'

    stages = {
        'source': Sage,
        'JavaScriptEvaluator_01': JSConvertMetrics,
        'ExpressionEvaluator_02': AddProperties,
        'destination': Destination
    }
