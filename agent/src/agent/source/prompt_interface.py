from abc import ABC, abstractmethod


class PromptInterface(ABC):
    @abstractmethod
    def prompt(self, default_config: dict, advanced: bool = False) -> dict:
        pass
