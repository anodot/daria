import json
import os

from agent import source
from agent.modules.logger import get_logger
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline

logger = get_logger(__name__)


class BaseConfigLoader:
    BASE_PIPELINE_CONFIGS_PATH = os.path.join('pipeline', 'config', 'base_pipelines')

    @classmethod
    def load_base_config(cls, pipeline: Pipeline):
        with open(cls._get_config_path(pipeline)) as f:
            data = json.load(f)
        return data['pipelineConfig']

    @classmethod
    def _get_config_path(cls, pipeline: Pipeline):
        return os.path.join(ROOT_DIR, cls.BASE_PIPELINE_CONFIGS_PATH, cls._get_configs()[pipeline.source.type])

    @classmethod
    def _get_configs(cls) -> dict:
        return {
            source.TYPE_INFLUX: 'influx_http.json',
            source.TYPE_MONGO: 'mongo_http.json',
            source.TYPE_KAFKA: 'kafka_http.json',
            source.TYPE_MYSQL: 'jdbc_http.json',
            source.TYPE_POSTGRES: 'jdbc_http.json',
            source.TYPE_ELASTIC: 'elastic_http.json',
            source.TYPE_SPLUNK: 'tcp_server_http.json',
            source.TYPE_DIRECTORY: 'directory_http.json',
            source.TYPE_SAGE: 'sage_http.json',
            source.TYPE_VICTORIA: 'victoria_http.json',
        }


class TestPipelineBaseConfigLoader(BaseConfigLoader):
    BASE_PIPELINE_CONFIGS_PATH = os.path.join('pipeline', 'test_pipelines')

    @classmethod
    def _get_configs(cls) -> dict:
        return {
            source.TYPE_INFLUX: 'test_influx_qwe093.json',
            source.TYPE_MONGO: 'test_mongo_rand847.json',
            source.TYPE_KAFKA: 'test_kafka_kjeu4334.json',
            source.TYPE_MYSQL: 'test_jdbc_pdsf4587.json',
            source.TYPE_POSTGRES: 'test_jdbc_pdsf4587.json',
            source.TYPE_ELASTIC: 'test_elastic_asdfs3245.json',
            source.TYPE_SPLUNK: 'test_tcp_server_jksrj322.json',
            source.TYPE_DIRECTORY: 'test_directory_ksdjfjk21.json',
            source.TYPE_SAGE: 'test_sage_jfhdkj.json',
        }


class BaseConfigHandler:
    stages_to_override = {}

    def __init__(self, pipeline: Pipeline, is_preview=False):
        self.config = {}
        self.pipeline = pipeline
        self.is_preview = is_preview

    def override_base_config(self, base_config, new_uuid=None, new_title=None):
        self.config = base_config
        if new_uuid:
            self.config['uuid'] = new_uuid
        if new_title:
            self.config['title'] = new_title

        self._override_pipeline_config()
        self._override_stages()
        self._set_labels()

        return self.config

    def _set_labels(self):
        self.config['metadata']['labels'] = [self.pipeline.source.type,
                                             self.pipeline.destination.TYPE]

    def _override_stages(self):
        for stage in self.config['stages']:
            if stage['instanceName'] in self.stages_to_override:
                stage_config = self.stages_to_override[stage['instanceName']](self.pipeline, stage).config
                for conf in stage['configuration']:
                    if conf['name'] in stage_config:
                        conf['value'] = stage_config[conf['name']]

    def _get_pipeline_config(self) -> dict:
        return {
            'TOKEN': self.pipeline.destination.token,
            'PROTOCOL': self.pipeline.destination.PROTOCOL_20,
            'ANODOT_BASE_URL': self.pipeline.destination.url,
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }

    def _override_pipeline_config(self):
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [{'key': key, 'value': val} for key, val in self._get_pipeline_config().items()]


class ConfigHandlerException(Exception):
    pass
