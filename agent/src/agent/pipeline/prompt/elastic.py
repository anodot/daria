
from .json import PromptConfigJson


class PromptConfigElastic(PromptConfigJson):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']
