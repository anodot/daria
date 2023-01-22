from agent import source
from agent.pipeline.json_builder import Builder


class ElasticBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'elastic'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        if 'query_file' in self.config:
            with open(self.config['query_file']) as f:
                self.config['query'] = f.read()
        return self.config
