from .base import BaseConfigHandler
from agent.modules.logger import get_logger

logger = get_logger(__name__)


class SchemaConfigHandler(BaseConfigHandler):
    def _get_pipeline_config(self) -> dict:
        pipeline_config = super()._get_pipeline_config()
        pipeline_config.update({
            'SCHEMA_ID': self.pipeline.get_schema_id(),
            'PROTOCOL': self.pipeline.destination.PROTOCOL_30
        })
        return pipeline_config
