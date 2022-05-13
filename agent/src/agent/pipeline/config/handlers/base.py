from abc import ABC, abstractmethod
from agent.modules import constants
from agent.modules.logger import get_logger
from agent.pipeline import Pipeline
from agent.pipeline.config.stages.base import Stage

logger = get_logger(__name__)


class ConfigHandler(ABC):
    stages_to_override = {}

    def __init__(self, pipeline: Pipeline, base_config: dict):
        self.config = base_config
        self.pipeline = pipeline
        self._check_pipeline()

    @abstractmethod
    def _check_pipeline(self):
        pass

    def override_base_config(self):
        self._override_pipeline_config()
        self._override_stages()
        self._set_labels()
        return self.config

    def _set_labels(self):
        self.config['metadata']['labels'] = [self.pipeline.source.type, self.pipeline.destination.TYPE]

    def _override_stages(self):
        for stage in self.config['stages']:
            if stage['instanceName'] in self.stages_to_override:
                stage_config = self._get_stage(stage).get_config()
                for conf in stage['configuration']:
                    if conf['name'] in stage_config:
                        conf['value'] = stage_config[conf['name']]

    def _get_stage(self, stage) -> Stage:
        return self.stages_to_override[stage['instanceName']](self.pipeline)

    def _override_pipeline_config(self):
        self.config['title'] = self.pipeline.name
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [{'key': key, 'value': val} for key, val in self._get_pipeline_config().items()]
            if config['name'] == 'retryAttempts':
                config['value'] = constants.STREAMSETS_MAX_RETRY_ATTEMPTS

    def _get_pipeline_config(self) -> dict:
        return {
            'TOKEN': self.pipeline.destination.token,
            'AUTH_TOKEN': self.pipeline.destination.auth_token.authentication_token,
            'PROTOCOL': self.pipeline.destination.PROTOCOL_20,
            'ANODOT_BASE_URL': self.pipeline.destination.url,
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }


class NoSchemaConfigHandler(ConfigHandler):
    def _check_pipeline(self):
        assert not self.pipeline.uses_schema()


class SchemaConfigHandler(ConfigHandler):
    def _get_pipeline_config(self) -> dict:
        pipeline_config = super()._get_pipeline_config()
        pipeline_config.update({
            'SCHEMA_ID': self.pipeline.get_schema_id(),
            'PROTOCOL': self.pipeline.destination.PROTOCOL_30
        })
        return pipeline_config

    def _check_pipeline(self):
        assert self.pipeline.uses_schema()


class RawConfigHandler(NoSchemaConfigHandler):
    def _get_pipeline_config(self) -> dict:
        return {
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }


class TestConfigHandler(NoSchemaConfigHandler):
    def _get_pipeline_config(self) -> dict:
        return {
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }
