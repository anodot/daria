from agent.pipeline.json_builder import Builder


class MongoBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'mongo'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        return self.config
