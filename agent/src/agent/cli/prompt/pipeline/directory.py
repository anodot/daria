import click
from .schemaless import PromptConfigSchemaless
from agent import pipeline


class PromptConfigDirectory(PromptConfigSchemaless):
    def prompt_config(self):
        self.config['uses_schema'] = True
        super().prompt_config()
        self.prompt_flush_bucket_size()

    def prompt_flush_bucket_size(self):
        self.pipeline.flush_bucket_size = click.prompt('Flush bucket size',
                                                       type=click.Choice([v.value for v in pipeline.FlushBucketSize]),
                                                       default=self.default_config.get(self.pipeline.FLUSH_BUCKET_SIZE))
