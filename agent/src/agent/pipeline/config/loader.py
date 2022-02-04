import json
import os

from abc import abstractmethod, ABC
from agent import source
from agent.modules.constants import ROOT_DIR
from agent.pipeline import Pipeline


class ConfigLoader(ABC):
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
        return os.path.join(
            ROOT_DIR, 'pipeline', 'config', cls.BASE_PIPELINE_CONFIGS_PATH, cls._get_config_file(pipeline)
        )

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
            source.TYPE_PROMETHEUS: 'promql.json',
            source.TYPE_SAGE: 'sage_http.json',
            source.TYPE_SNMP: 'snmp.json',
            source.TYPE_SPLUNK: 'tcp_server_http.json',
            source.TYPE_SOLARWINDS: 'solarwinds.json',
            source.TYPE_THANOS: 'promql.json',
            source.TYPE_TOPOLOGY: 'topology.json',
            source.TYPE_VICTORIA: 'promql.json',
            source.TYPE_ZABBIX: 'zabbix_http.json',
        }[pipeline.source.type]


class NoSchemaConfigLoader(ConfigLoader):
    def _check_pipeline(self, pipeline_: Pipeline):
        assert not pipeline_.uses_schema


class SchemaConfigLoader(ConfigLoader):
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
            source.TYPE_PROMETHEUS: 'promql_schema.json',
            source.TYPE_SAGE: 'sage_schema.json',
            source.TYPE_SNMP: 'snmp_schema.json',
            source.TYPE_THANOS: 'promql_schema.json',
            source.TYPE_VICTORIA: 'promql_schema.json',
        }[pipeline.source.type]


class RawConfigLoader(ConfigLoader):
    BASE_PIPELINE_CONFIGS_PATH = 'base_pipelines/raw'

    def _check_pipeline(self, pipeline_: Pipeline):
        pass


class TestPipelineConfigLoader(ConfigLoader):
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
