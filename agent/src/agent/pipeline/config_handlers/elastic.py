import csv

from .kafka import KafkaConfigHandler
from agent.logger import get_logger
from .expression_parser import condition

logger = get_logger(__name__)


class ElasticConfigHandler(KafkaConfigHandler):
    def override_stages(self):
        self.update_source_configs()

        self.update_stages()

        self.update_destination_config()
