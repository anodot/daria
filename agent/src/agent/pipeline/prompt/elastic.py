
from .kafka import PromptConfigKafka


class PromptConfigElastic(PromptConfigKafka):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']
