import json
from .json import JsonConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class ElasticConfigHandler(JsonConfigHandler):
    def override_stages(self):
        self.client_config['source']['config']['conf.query'] = json.dumps(self.client_config['source']['config']['conf.query'])
        super().override_stages()
