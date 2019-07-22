from .json import JsonConfigHandler
from agent.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)


class MongoConfigHandler(JsonConfigHandler):

    def set_initial_offset(self):
        source_config = self.client_config['source']['config']

        if source_config['configBean.initialOffset'].isdigit():
            timestamp = datetime.now() - timedelta(days=int(source_config['configBean.initialOffset']))
            source_config['configBean.initialOffset'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def update_source_configs(self):
        if self.client_config['source']['config']['configBean.offsetType'] != 'STRING':
            self.set_initial_offset()
        super().update_source_configs()
