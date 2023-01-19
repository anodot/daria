from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, TestConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class ElasticConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }


class ElasticSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.elastic.ElasticScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
        'destination_watermark_with_metrics': stages.destination.WatermarkWithMetricsDestination,
    }


class TestElasticConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
    }
