from agent.pipeline.json_builder import Builder
from agent.pipeline.json_builder.json_builder import EventsBuilder


class DirectoryBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'directory'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        return self.config


class DirectoryEventsBuilder(EventsBuilder):
    VALIDATION_SCHEMA_FILE_NAME = 'directory'
