from agent.pipeline.json_builder import Builder


class TcpBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'tcp_server'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        return self.config
