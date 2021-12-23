import json
import os

from abc import ABC, abstractmethod
from agent import source
from agent.modules import constants
from agent.modules.logger import get_logger
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline
from agent.pipeline.config.stages.base import Stage

logger = get_logger(__name__)


class BaseConfigLoader(ABC):
    BASE_PIPELINE_CONFIGS_PATH = 'base_pipelines'

    @abstractmethod
    def _check_pipeline(self, pipeline_: Pipeline):
        pass

    @classmethod
    def load_base_config(cls, pipeline: Pipeline) -> dict:
        with open(cls._get_config_path(pipeline)) as f:
            data = json.load(f)
        return data['pipelineConfig']

    @classmethod
    def _get_config_path(cls, pipeline: Pipeline):
        return os.path.join(ROOT_DIR, 'pipeline', 'config', cls.BASE_PIPELINE_CONFIGS_PATH,
                            cls._get_config_file(pipeline))

    @classmethod
    def _get_config_file(cls, pipeline: Pipeline) -> str:
        return {
            source.TYPE_CACTI: 'cacti.json',
            source.TYPE_CLICKHOUSE: 'jdbc.json',
            source.TYPE_ELASTIC: 'elastic_http.json',
            source.TYPE_INFLUX: 'influx_http.json',
            source.TYPE_KAFKA: 'kafka_http.json',
            source.TYPE_MONGO: 'mongo_http.json',
            source.TYPE_MYSQL: 'jdbc.json',
            source.TYPE_POSTGRES: 'jdbc.json',
            source.TYPE_PROMETHEUS: 'promql_http.json',
            source.TYPE_SAGE: 'sage_http.json',
            source.TYPE_SNMP: 'snmp.json',
            source.TYPE_SPLUNK: 'tcp_server_http.json',
            source.TYPE_SOLARWINDS: 'solarwinds.json',
            source.TYPE_THANOS: 'promql_http.json',
            source.TYPE_VICTORIA: 'promql_http.json',
            source.TYPE_ZABBIX: 'zabbix_http.json',
        }[pipeline.source.type]


class NoSchemaConfigLoader(BaseConfigLoader):
    def _check_pipeline(self, pipeline_: Pipeline):
        assert not pipeline_.uses_schema


class SchemaBaseConfigLoader(BaseConfigLoader):
    def _check_pipeline(self, pipeline_: Pipeline):
        assert pipeline_.uses_schema

    @classmethod
    def _get_config_file(cls, pipeline: Pipeline) -> str:
        return {
            source.TYPE_CLICKHOUSE: 'jdbc_schema.json',
            source.TYPE_DIRECTORY: 'directory_schema.json',
            source.TYPE_DATABRICKS: 'jdbc_schema.json',
            source.TYPE_INFLUX: 'influx_schema.json',
            source.TYPE_INFLUX_2: 'influx2_schema.json',
            source.TYPE_KAFKA: 'kafka_http_schema.json',
            source.TYPE_MYSQL: 'jdbc_schema.json',
            source.TYPE_ORACLE: 'jdbc_schema.json',
            source.TYPE_OBSERVIUM: 'observium_schema.json',
            source.TYPE_POSTGRES: 'jdbc_schema.json',
            source.TYPE_SNMP: 'snmp_schema.json',
        }[pipeline.source.type]


class RawConfigLoader(BaseConfigLoader):
    BASE_PIPELINE_CONFIGS_PATH = 'base_pipelines/raw'

    def _check_pipeline(self, pipeline_: Pipeline):
        pass


class TestPipelineBaseConfigLoader(BaseConfigLoader):
    BASE_PIPELINE_CONFIGS_PATH = 'test_pipelines'

    def _check_pipeline(self, pipeline_: Pipeline):
        pass

    @classmethod
    def _get_config_file(cls, pipeline: Pipeline) -> str:
        return {
            source.TYPE_CLICKHOUSE: 'test_jdbc_pdsf4587.json',
            source.TYPE_DIRECTORY: 'test_directory_ksdjfjk21.json',
            source.TYPE_DATABRICKS: 'test_jdbc_pdsf4587.json',
            source.TYPE_ELASTIC: 'test_elastic_asdfs3245.json',
            source.TYPE_INFLUX: 'test_influx_qwe093.json',
            source.TYPE_INFLUX_2: 'test_influx2_x1ccwlf.json',
            source.TYPE_MONGO: 'test_mongo_rand847.json',
            source.TYPE_KAFKA: 'test_kafka_kjeu4334.json',
            source.TYPE_MYSQL: 'test_jdbc_pdsf4587.json',
            source.TYPE_POSTGRES: 'test_jdbc_pdsf4587.json',
            source.TYPE_PROMETHEUS: 'test_promql_m7p99ao.json',
            source.TYPE_OBSERVIUM: 'test_observium_rjjd1fm.json',
            source.TYPE_ORACLE: 'test_jdbc_pdsf4587.json',
            source.TYPE_SAGE: 'test_sage_jfhdkj.json',
            source.TYPE_SPLUNK: 'test_tcp_server_jksrj322.json',
            source.TYPE_SOLARWINDS: 'test_solarwinds_jksrj322.json',
            source.TYPE_THANOS: 'test_promql_m7p99ao.json',
            source.TYPE_VICTORIA: 'test_promql_m7p99ao.json',
            source.TYPE_ZABBIX: 'test_zabbix_jfhdkj.json',
        }[pipeline.source.type]


class BaseConfigHandler(ABC):
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
            'PROTOCOL': self.pipeline.destination.PROTOCOL_20,
            'ANODOT_BASE_URL': self.pipeline.destination.url,
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }


class NoSchemaConfigHandler(BaseConfigHandler):
    def _check_pipeline(self):
        assert not self.pipeline.uses_schema


class SchemaConfigHandler(BaseConfigHandler):
    def _get_pipeline_config(self) -> dict:
        pipeline_config = super()._get_pipeline_config()
        pipeline_config.update({
            'SCHEMA_ID': self.pipeline.get_schema_id(),
            'PROTOCOL': self.pipeline.destination.PROTOCOL_30
        })
        return pipeline_config

    def _check_pipeline(self):
        assert self.pipeline.uses_schema


class BaseRawConfigHandler(BaseConfigHandler):
    def _check_pipeline(self):
        pass

    def _get_pipeline_config(self) -> dict:
        return {
            'AGENT_URL': self.pipeline.streamsets.agent_external_url,
        }
