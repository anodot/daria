import click
from .schemaless import PromptConfigSchemaless
from agent.pipeline import pipeline


class PromptConfigDirectory(PromptConfigSchemaless):
    def prompt_config(self):
        if not self.pipeline.destination.access_key:
            raise click.UsageError('No api key configured. Please configure api key using `agent destination` command')
        super().prompt_config()
        self.prompt_flush_bucket_size()

    def prompt_flush_bucket_size(self):
        self.pipeline.flush_bucket_size = click.prompt('Flush bucket size',
                                                       type=click.Choice([v.value for v in pipeline.FlushBucketSize]),
                                                       default=self.default_config.get(self.pipeline.FLUSH_BUCKET_SIZE))
