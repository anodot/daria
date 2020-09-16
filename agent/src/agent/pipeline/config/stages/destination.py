from .base import Stage


class Destination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config
