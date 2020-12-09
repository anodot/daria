from .schemaless import PromptConfigSchemaless


class PromptConfigMongo(PromptConfigSchemaless):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']

    def set_timezone(self):
        pass
