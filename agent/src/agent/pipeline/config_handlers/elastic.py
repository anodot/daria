import json
from .json import JsonConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class ElasticConfigHandler(JsonConfigHandler):
    pass
