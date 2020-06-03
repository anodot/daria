import json
from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class TCPConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'tcp_server_http.json'
