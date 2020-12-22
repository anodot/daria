from .base import Stage


class Source(Stage):
    def _get_config(self) -> dict:
        return {**self.pipeline.source.config, **self.pipeline.override_source}
