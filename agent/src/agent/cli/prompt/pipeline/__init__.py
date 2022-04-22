from agent import source
from agent.pipeline import Pipeline, PipelineException
from .base import Prompter
from .jdbc import JDBCPrompter
from .kafka import KafkaPrompter
from .mongo import MongoPrompter
from .elastic import ElasticPrompter
from .solarwinds import SolarWindsPrompter
from .tcp import TCPPrompter
from .sage import SagePrompter
from .zabbix import ZabbixPrompter


def get_prompter(pipeline_: Pipeline, default_config: dict, advanced: bool) -> Prompter:
    prompters = {
        source.TYPE_CLICKHOUSE: JDBCPrompter,
        source.TYPE_ELASTIC: ElasticPrompter,
        source.TYPE_KAFKA: KafkaPrompter,
        source.TYPE_MONGO: MongoPrompter,
        source.TYPE_MYSQL: JDBCPrompter,
        source.TYPE_POSTGRES: JDBCPrompter,
        source.TYPE_SAGE: SagePrompter,
        source.TYPE_SPLUNK: TCPPrompter,
        source.TYPE_SOLARWINDS: SolarWindsPrompter,
        source.TYPE_ZABBIX: ZabbixPrompter,
    }
    try:
        return prompters[pipeline_.source.type](pipeline_, default_config, advanced)
    except KeyError as e:
        raise PipelineException(f'No prompter available for Pipeline with source type `{pipeline_.source.type}`') from e
