from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class JDBCConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'jdbc_http.json'
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/jdbc_{destination_name}.json'

    stages_to_override = {
        'source': stages.jdbc_source.JDBCSourceStage,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }
