from agent import source
from .base import Prompter
from .directory import DirectoryPrompter
from .elastic import ElasticPrompter
from .influx import InfluxPrompter
from .jdbc import JDBCPrompter
from .kafka import KafkaBuilder
from .mongo import MongoPrompter
from .sage import SagePrompter
from .tcp import TCPPrompter
from .victoria import VictoriaPrompter
from .zabbix import ZabbixPrompter
from .cacti import CactiPrompter


def get_prompter(source_: source.Source) -> Prompter:
    types = {
        source.TYPE_INFLUX: InfluxPrompter,
        source.TYPE_KAFKA: KafkaBuilder,
        source.TYPE_MONGO: MongoPrompter,
        source.TYPE_MYSQL: JDBCPrompter,
        source.TYPE_POSTGRES: JDBCPrompter,
        source.TYPE_ELASTIC: ElasticPrompter,
        source.TYPE_SPLUNK: TCPPrompter,
        source.TYPE_DIRECTORY: DirectoryPrompter,
        source.TYPE_SAGE: SagePrompter,
        source.TYPE_VICTORIA: VictoriaPrompter,
        source.TYPE_ZABBIX: ZabbixPrompter,
        source.TYPE_CACTI: CactiPrompter,
    }
    if source_.type not in source.types:
        raise ValueError(f'{source_.type} isn\'t supported')
    return types[source_.type](source_)
