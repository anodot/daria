from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config import schema
from agent.pipeline.config.stages import JSConvertMetrics, AddProperties30, Filtering, Destination, Source, \
    SendWatermark

logger = get_logger(__name__)


class DirectoryConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'directory_http.json'

    stages = {
        'source': Source,
        'JavaScriptEvaluator_01': JSConvertMetrics,
        'ExpressionEvaluator_02': AddProperties30,
        'ExpressionEvaluator_03': Filtering,
        'process_finish_file_event': SendWatermark,
        'destination': Destination,
        'destination_watermark': Destination,
    }

    def get_pipeline_config(self) -> dict:
        schema_definition = schema.update(self.pipeline)
        self.pipeline.config.update(schema_definition)
        pipeline_config = super().get_pipeline_config()
        pipeline_config.update({
            'SCHEMA_ID': schema_definition['schema']['id'],
            'PROTOCOL': self.pipeline.destination.PROTOCOL_30
        })
        return pipeline_config
