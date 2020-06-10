import click
from .schemaless import PromptConfigSchemaless


class PromptConfigDirectory(PromptConfigSchemaless):
    def set_config(self):
        if not self.pipeline.destination.access_key:
            raise click.UsageError('No api key configured. Please configure api key using `agent destination` command')
        super().set_config()
