from agent.pipeline.config.stages.base import Stage


class Source(Stage):
    def get_config(self) -> dict:
        return {**self.pipeline.source.config, **self.pipeline.override_source}
