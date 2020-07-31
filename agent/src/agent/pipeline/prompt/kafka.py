import click
from .schemaless import PromptConfigSchemaless
from agent import source


class PromptConfigKafka(PromptConfigSchemaless):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']
    target_types = ['counter', 'gauge', 'running_counter']
    pass

    def set_config(self):
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_timestamp()
        self.set_dimensions()
        self.set_consumer_group()
        self.set_static_properties()
        self.set_tags()
        self.filter()
        self.transform()

    def set_consumer_group(self):
        self.pipeline.override_source[source.KafkaSource.CONFIG_CONSUMER_GROUP] =\
            click.prompt('Consumer group name', self._get_default_consumer_group())

    def _get_default_consumer_group(self) -> str:
        if source.KafkaSource.CONFIG_CONSUMER_GROUP in self.pipeline.override_source:
            return self.pipeline.override_source[source.KafkaSource.CONFIG_CONSUMER_GROUP]
        return "agent_" + self.pipeline.id
