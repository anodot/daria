import click

from .schemaless import SchemalessPrompter
from agent import pipeline


class DirectoryPrompter(SchemalessPrompter):
    def prompt_config(self):
        self.config['uses_schema'] = True
        super().prompt_config()
        self.prompt_flush_bucket_size()

    def prompt_flush_bucket_size(self):
        self.pipeline.flush_bucket_size = click.prompt(
            'Flush bucket size',
            type=click.Choice(pipeline.FlushBucketSize.VALUES),
            default=self.default_config.get(self.pipeline.FLUSH_BUCKET_SIZE)
        )
