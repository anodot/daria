from agent.pipeline.json_builder import Builder


class PRTGBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'prtg'

    def _set_timestamp(self):
        self.config['timestamp'] = {
            'type': 'unix',
            'name': 'timestamp_unix',
        }

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        self._set_timestamp()
        self.config['uses_schema'] = True
        return self.config
