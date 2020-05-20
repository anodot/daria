import click
from .schemaless import PromptConfigSchemaless
from agent.source import KafkaSource


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
        self.pipeline.source.config[KafkaSource.CONFIG_CONSUMER_GROUP] =\
            click.prompt('Consumer group name', "agent_" + self.pipeline.id)
