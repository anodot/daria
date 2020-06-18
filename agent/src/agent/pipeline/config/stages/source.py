from .base import Stage


class Source(Stage):
    def get_config(self) -> dict:
        return {**self.pipeline.source.config, **self.pipeline.get_override_source()}
