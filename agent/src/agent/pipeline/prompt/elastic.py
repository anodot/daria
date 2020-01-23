import click
import json

from agent.tools import infinite_retry
from .base import PromptConfig


class PromptConfigElastic(PromptConfig):
    def set_index(self):
        self.pipeline.source.config['index'] = click.prompt('Index', type=click.STRING, default=self.default_config.get('index', ''))

