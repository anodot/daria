import click
from .schemaless import PromptConfigSchemaless
from agent.source import KafkaSource
from .. import Pipeline


class PromptConfigKafka(PromptConfigSchemaless):
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
        default_consumer_group = self.get_default_consumer_group()
        self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] =\
            click.prompt('Consumer group name', default_consumer_group)

    def get_default_consumer_group(self) -> str:
        values = self.default_config.get(Pipeline.OVERRIDE_SOURCE)
        if not values or not values.get(KafkaSource.CONFIG_CONSUMER_GROUP):
            return "agent_" + self.pipeline.id
        return values[KafkaSource.CONFIG_CONSUMER_GROUP]
