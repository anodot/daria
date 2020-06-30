from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent.pipeline import Pipeline


class Stage(ABC):
    def __init__(self, pipeline: Pipeline, sdc_stage: dict):
        self.pipeline = pipeline
        self.sdc_stage = sdc_stage
        self.config = self.get_config()

    @abstractmethod
    def get_config(self) -> dict:
        pass

    def update_sdc_stage(self):
        for conf in self.sdc_stage['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]
