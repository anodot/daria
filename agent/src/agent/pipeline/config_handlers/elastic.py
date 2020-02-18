import json
from .json import JsonConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class ElasticConfigHandler(JsonConfigHandler):
    def override_stages(self):
        with open(self.pipeline.config['query_file'], 'r') as f:
            self.client_config['source']['config'][self.pipeline.source.CONFIG_QUERY] = f.read()

        super().override_stages()
