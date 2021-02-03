import click

from abc import ABC, abstractmethod
from agent import source


class Builder(ABC):
    def __init__(self, source_: source.Source):
        self.source = source_
        self.validator = source.validator.get_validator(self.source)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass

    def prompt_query_timeout(self, default_config, advanced):
        if advanced:
            self.source.config['query_timeout'] = click.prompt(
                'Query timeout (in seconds)',
                type=click.INT,
                default=default_config.get('query_timeout', 15)
            ).strip()
