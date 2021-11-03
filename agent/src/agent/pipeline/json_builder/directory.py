from agent.pipeline.json_builder import Builder


class DirectoryBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'directory'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        return self.config
