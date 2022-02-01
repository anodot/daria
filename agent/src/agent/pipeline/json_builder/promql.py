from agent.pipeline.json_builder import Builder


class PromQLBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'promql'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'name': 'timestamp', 'type': 'unix'}
        return self.config
