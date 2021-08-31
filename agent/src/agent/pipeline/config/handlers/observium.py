from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


# todo
class ObserviumConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'event_add_metadata_tags': stages.expression_evaluator.AddMetadataTags,
        'events_destination': stages.destination.EventsDestination,
        'destination': stages.destination.Destination
    }
