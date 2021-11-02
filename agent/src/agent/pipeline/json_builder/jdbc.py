from agent.pipeline.json_builder import Builder


class JDBCBuilder(Builder):
    # todo is it correct? used to be ../jdbc
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'


class JDBCRawBuilder(Builder):
    # todo is it correct? used to be ../jdbc
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'
