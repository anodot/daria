from .base import Stage


class Destination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentOffsetUrl': self.pipeline.streamsets.agent_external_url + '/pipeline-offset/${pipeline:id()}',
            self.pipeline.destination.CONFIG_ENABLE_REQUEST_LOGGING: self.pipeline.destination.if_logs_enabled,
            **self.pipeline.destination.config
        }


class WatermarkDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config


class EventsDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config
