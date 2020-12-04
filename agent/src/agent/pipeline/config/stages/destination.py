from .base import Stage


class Destination(Stage):
    def _get_config(self) -> dict:
        return {
            'conf.agentOffsetUrl': self.pipeline.streamsets.agent_external_url + '/pipeline-offset/${pipeline:id()}'
        }


class WatermarkDestination(Stage):
    def _get_config(self) -> dict:
        return self.pipeline.destination.config


class EventsDestination(Stage):
    def _get_config(self) -> dict:
        return self.pipeline.destination.config
