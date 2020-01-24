
from .kafka import PromptConfigKafka


class PromptConfigElastic(PromptConfigKafka):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']

    def set_config(self):
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

