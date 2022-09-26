from agent.pipeline.json_builder import Builder
from agent.pipeline.json_builder.json_builder import EventsBuilder


class JDBCBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'


class JDBCRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'


class JDBCEventBuilder(EventsBuilder):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'
