from agent.pipeline.json_builder import Builder


class SageBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'sage'

    def _load_config(self):
        super()._load_config()
        if 'query_file' in self.config:
            with open(self.config['query_file']) as f:
                self.config['query'] = f.read()
        return self.config
