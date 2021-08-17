import click
from .schemaless import SchemalessPrompter
from agent import source


class KafkaPrompter(SchemalessPrompter):
    timestamp_types = ['datetime', 'string', 'unix', 'unix_ms']
    target_types = ['counter', 'gauge', 'running_counter']

    def prompt_config(self):
        self.data_preview()
        self.set_values()
        self.prompt_measurement_names()
        self.prompt_timestamp()
        self.set_dimensions()
        self.set_consumer_group()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.filter()
        self.set_transform()
        self.set_uses_schema()

    def set_consumer_group(self):
        self.config['override_source'][source.KafkaSource.CONFIG_CONSUMER_GROUP] =\
            click.prompt('Consumer group name', self._get_default_consumer_group())

    def _get_default_consumer_group(self) -> str:
        if source.KafkaSource.CONFIG_CONSUMER_GROUP in self.config['override_source']:
            return self.config['override_source'][source.KafkaSource.CONFIG_CONSUMER_GROUP]
        return "agent_" + self.pipeline.name
