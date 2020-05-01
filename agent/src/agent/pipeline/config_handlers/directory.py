import json
from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class DirectoryConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'directory_http.json'

    def create_schema(self):
        pass
