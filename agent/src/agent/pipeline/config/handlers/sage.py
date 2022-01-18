from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline import pipeline
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class SageConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.sage.SageScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'event_add_metadata_tags': stages.expression_evaluator.AddMetadataTags,
        'events_destination': stages.destination.EventsDestination,
        'destination': stages.destination.Destination
    }

    def _override_stages(self):
        self.pipeline.config['timestamp'] = {
            'name': '@timestamp',
            'type': pipeline.TimestampType.UTC_STRING.value
        }
        super()._override_stages()


class SageSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.sage.SageScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'event_add_metadata_tags': stages.expression_evaluator.AddMetadataTags,
        'destination': stages.destination.Destination
    }
