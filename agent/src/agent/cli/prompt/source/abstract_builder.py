from abc import ABC, abstractmethod
from agent import source


class Builder(ABC):
    def __init__(self, source_: source.Source):
        self.source = source_
        self.validator = source.validator.get_validator(self.source)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass
