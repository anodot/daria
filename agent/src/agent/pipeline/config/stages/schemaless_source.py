from .base import Stage
from agent import source


class SchemalessSource(Stage):
    def get_config(self) -> dict:
        conf = {**self.pipeline.source.config, **self.pipeline.override_source}
        if self.pipeline.source.config.get(source.SchemalessSource.CONFIG_GROK_PATTERN_FILE):
            with open(self.pipeline.source.config[source.SchemalessSource.CONFIG_GROK_PATTERN_FILE]) as f:
                conf[source.SchemalessSource.CONFIG_GROK_PATTERN_DEFINITION] = f.read()
        return conf
