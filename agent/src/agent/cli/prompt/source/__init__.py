from agent import source
from .base import Prompter
from .directory import DirectoryPrompter
from .elastic import ElasticPrompter
from .influx import InfluxPrompter, Influx2Prompter
from .jdbc import JDBCPrompter
from .kafka import KafkaBuilder
from .mongo import MongoPrompter
from .sage import SagePrompter
from .solarwinds import SolarWindsPrompter
from .tcp import TCPPrompter
from .victoria import VictoriaPrompter
from .zabbix import ZabbixPrompter


def get_prompter(source_: source.Source) -> Prompter:
    types = {
        source.TYPE_CLICKHOUSE: JDBCPrompter,
        source.TYPE_DIRECTORY: DirectoryPrompter,
        source.TYPE_ELASTIC: ElasticPrompter,
        source.TYPE_INFLUX: InfluxPrompter,
        source.TYPE_INFLUX_2: Influx2Prompter,
        source.TYPE_KAFKA: KafkaBuilder,
        source.TYPE_MONGO: MongoPrompter,
        source.TYPE_MYSQL: JDBCPrompter,
        source.TYPE_POSTGRES: JDBCPrompter,
        source.TYPE_SAGE: SagePrompter,
        source.TYPE_SPLUNK: TCPPrompter,
        source.TYPE_SOLARWINDS: SolarWindsPrompter,
        source.TYPE_VICTORIA: VictoriaPrompter,
        source.TYPE_ZABBIX: ZabbixPrompter,
    }
    if source_.type not in source.types:
        raise ValueError(f'{source_.type} isn\'t supported')
    return types[source_.type](source_)
