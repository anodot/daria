from agent import pipeline, source
from agent.pipeline import Pipeline
from .json_builder import Builder
from .cacti import CactiBuilder
from .directory import DirectoryBuilder
from .elastic import ElasticBuilder
from .influx import InfluxBuilder, Influx2Builder
from .jdbc import JDBCBuilder, JDBCRawBuilder
from .kafka import KafkaBuilder
from .mongo import MongoBuilder
from .observium import ObserviumBuilder
from .promql import PromQLBuilder
from .sage import SageBuilder
from .snmp import SNMPBuilder, SNMPRawBuilder
from .solarwinds import SolarWindsClientData
from .tcp import TcpBuilder
from .zabbix import ZabbixBuilder
from .json_builder import build, build_raw, build_using_file, build_raw_using_file, build_multiple
from .json_builder import edit, edit_using_file, edit_multiple, extract_configs


def get(pipeline_: Pipeline, config: dict, is_edit=False) -> Builder:
    if isinstance(pipeline_, pipeline.RawPipeline):
        return _get_raw_builder(pipeline_, config, is_edit)
    return _get_builder(pipeline_, config, is_edit)


def _get_builder(pipeline_: Pipeline, config: dict, is_edit: bool) -> Builder:
    loaders = {
        source.TYPE_CACTI: CactiBuilder,
        source.TYPE_CLICKHOUSE: JDBCBuilder,
        source.TYPE_DIRECTORY: DirectoryBuilder,
        source.TYPE_ELASTIC: ElasticBuilder,
        source.TYPE_INFLUX: InfluxBuilder,
        source.TYPE_INFLUX_2: Influx2Builder,
        source.TYPE_KAFKA: KafkaBuilder,
        source.TYPE_MONGO: MongoBuilder,
        source.TYPE_MYSQL: JDBCBuilder,
        source.TYPE_ORACLE: JDBCBuilder,
        source.TYPE_POSTGRES: JDBCBuilder,
        source.TYPE_PROMETHEUS: PromQLBuilder,
        source.TYPE_OBSERVIUM: ObserviumBuilder,
        source.TYPE_SAGE: SageBuilder,
        source.TYPE_SNMP: SNMPBuilder,
        source.TYPE_SOLARWINDS: SolarWindsClientData,
        source.TYPE_SPLUNK: TcpBuilder,
        source.TYPE_THANOS: PromQLBuilder,
        source.TYPE_VICTORIA: PromQLBuilder,
        source.TYPE_ZABBIX: ZabbixBuilder,
    }
    return loaders[pipeline_.source.type](pipeline_, config, is_edit)


def _get_raw_builder(pipeline_: Pipeline, config: dict, is_edit: bool) -> Builder:
    loaders = {
        source.TYPE_CLICKHOUSE: JDBCRawBuilder,
        source.TYPE_MYSQL: JDBCRawBuilder,
        source.TYPE_POSTGRES: JDBCRawBuilder,
        source.TYPE_SNMP: SNMPRawBuilder,
    }
    return loaders[pipeline_.source.type](pipeline_, config, is_edit)