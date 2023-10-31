from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, RawConfigHandler
from agent.pipeline.config.handlers.base import TestConfigHandler, SchemaConfigHandler, ConfigHandler

logger = get_logger(__name__)


class JDBCSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc.JDBCOffsetScript,
        'source': stages.source.jdbc.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }


class JDBCConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc.JDBCOffsetScript,
        'source': stages.source.jdbc.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }


class JDBCRawConfigHandler(RawConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc.JDBCOffsetScript,
        'source': stages.source.jdbc.JDBCSource,
        'JythonEvaluator_01': stages.jdbc.JDBCRawTransformScript,
        'HTTPClient_01': stages.destination.HttpDestination,
    }


class JDBCEventsConfigHandler(ConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc.JDBCOffsetScript,
        'source': stages.source.jdbc.JDBCSource,
        'JythonEvaluator_01': stages.jython.JDBCCreateEvents,
        'JythonEvaluator_02': stages.destination.AnodotEventsDestination,
    }

    def _check_pipeline(self):
        pass


class TestJDBCConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.jdbc.JDBCSource,
    }
