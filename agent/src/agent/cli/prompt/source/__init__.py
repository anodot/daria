from agent import source
from .base import Prompter
from .elastic import ElasticPrompter
from .jdbc import JDBCPrompter
from .kafka import KafkaBuilder
from .mongo import MongoPrompter
from .sage import SagePrompter
from .solarwinds import SolarWindsPrompter
from .tcp import TCPPrompter
from .zabbix import ZabbixPrompter


def get_prompter(source_: source.Source) -> Prompter:
    types = {
        source.TYPE_CLICKHOUSE: JDBCPrompter,
        source.TYPE_ELASTIC: ElasticPrompter,
        source.TYPE_MONGO: MongoPrompter,
        source.TYPE_MSSQL: JDBCPrompter,
        source.TYPE_MYSQL: JDBCPrompter,
        source.TYPE_POSTGRES: JDBCPrompter,
        source.TYPE_SAGE: SagePrompter,
        source.TYPE_SOLARWINDS: SolarWindsPrompter,
        source.TYPE_ZABBIX: ZabbixPrompter,
    }
    if source_.type not in source.types:
        raise ValueError(f'{source_.type} isn\'t supported')
    return types[source_.type](source_)
