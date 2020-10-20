from agent.modules.constants import AGENT_URL
from .base import Stage


class Destination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentOffsetUrl': f'{AGENT_URL}/pipeline-offset/'
        }


class WatermarkDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config


class EventsDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config
