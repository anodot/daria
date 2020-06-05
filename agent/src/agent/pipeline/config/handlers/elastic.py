from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class ElasticConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'elastic_http.json'

    def override_stages(self):
        with open(self.pipeline.config['query_file']) as f:
            self.pipeline.source.config[self.pipeline.source.CONFIG_QUERY] = f.read()
        super().override_stages()
