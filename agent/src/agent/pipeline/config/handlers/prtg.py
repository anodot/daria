import json

from agent.modules import tools
from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import TestConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class PRTGSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.prtg.PRTGSource,
        'jython_transform_records': stages.influx.JythonTransformRecords,
        'js_create_metrics': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'filtering': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }
