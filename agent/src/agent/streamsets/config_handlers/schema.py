from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import schema
from ... import pipeline

logger = get_logger(__name__)


class SchemaConfigHandler(BaseConfigHandler):
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
