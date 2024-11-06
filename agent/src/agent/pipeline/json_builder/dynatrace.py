from agent.pipeline.json_builder import Builder


class DynatraceBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'dynatrace'

    def _load_config(self):
        super()._load_config()
        if 'timestamp' not in self.config:
            self.config['timestamp'] = {'type': 'utc_string', 'name': '@timestamp'}
        return self.config
