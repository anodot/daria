from .schemaless import PromptConfigSchemaless


class PromptConfigKafka(PromptConfigSchemaless):
    target_types = ['counter', 'gauge', 'running_counter']
    pass
