from .schemaless import SchemalessPrompter


class MongoPrompter(SchemalessPrompter):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']

    def set_timezone(self):
        pass
