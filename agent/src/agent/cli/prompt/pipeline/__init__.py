from agent import source
from agent.pipeline import Pipeline
from .base import Prompter
from .influx import InfluxPrompter, Influx2Prompter
from .jdbc import JDBCPrompter
from .kafka import KafkaPrompter
from .mongo import MongoPrompter
from .elastic import ElasticPrompter
from .solarwinds import SolarWindsPrompter
from .tcp import TCPPrompter
from .sage import SagePrompter
from .victoria import VictoriaPrompter
from .zabbix import ZabbixPrompter


def get_prompter(pipeline_: Pipeline, default_config: dict, advanced: bool) -> Prompter:
    prompters = {
        source.TYPE_CLICKHOUSE: JDBCPrompter,
        source.TYPE_ELASTIC: ElasticPrompter,
        source.TYPE_INFLUX: InfluxPrompter,
        source.TYPE_INFLUX_2: Influx2Prompter,
        source.TYPE_KAFKA: KafkaPrompter,
        source.TYPE_MONGO: MongoPrompter,
        source.TYPE_MYSQL: JDBCPrompter,
        source.TYPE_POSTGRES: JDBCPrompter,
        source.TYPE_SAGE: SagePrompter,
        source.TYPE_SPLUNK: TCPPrompter,
        source.TYPE_SOLARWINDS: SolarWindsPrompter,
        source.TYPE_VICTORIA: VictoriaPrompter,
        source.TYPE_ZABBIX: ZabbixPrompter,
    }
    return prompters[pipeline_.source.type](pipeline_, default_config, advanced)
