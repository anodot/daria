from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import schema
from agent.pipeline.config import stages
from agent import pipeline

logger = get_logger(__name__)


class DirectoryConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'process_finish_file_event': stages.expression_evaluator.SendWatermark,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }

    def _get_pipeline_config(self) -> dict:
        if not isinstance(self.pipeline, pipeline.TestPipeline):
            schema_definition = schema.update(self.pipeline)
            self.pipeline.schema = schema_definition
            schema_id = schema_definition['id']
        else:
            schema_id = 'preview'

        pipeline_config = super()._get_pipeline_config()
        pipeline_config.update({
            'SCHEMA_ID': schema_id,
            'PROTOCOL': self.pipeline.destination.PROTOCOL_30
        })
        return pipeline_config
