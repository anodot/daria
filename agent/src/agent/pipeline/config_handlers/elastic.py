from .kafka import KafkaConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class ElasticConfigHandler(KafkaConfigHandler):
    pass
