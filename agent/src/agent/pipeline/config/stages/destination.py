from .base import Stage


class Destination(Stage):
    def get_config(self) -> dict:
        self.pipeline.destination.config.pop(self.pipeline.destination.CONFIG_RESOURCE_URL, None)
        return self.pipeline.destination.config
