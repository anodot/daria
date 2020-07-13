from agent import source
from .abstract_builder import Builder
from .directory import DirectorySourceBuilder
from .elastic import ElasticSourceBuilder
from .influx import InfluxSourceBuilder
from .jdbc import JDBCSourceBuilder
from .kafka import KafkaSourceBuilder
from .mongo import MongoSourceBuilder
from .sage import SageSourceBuilder
from .tcp import TCPSourceBuilder

types = {
    source.TYPE_INFLUX: InfluxSourceBuilder,
    source.TYPE_KAFKA: KafkaSourceBuilder,
    source.TYPE_MONGO: MongoSourceBuilder,
    source.TYPE_MYSQL: JDBCSourceBuilder,
    source.TYPE_POSTGRES: JDBCSourceBuilder,
    source.TYPE_ELASTIC: ElasticSourceBuilder,
    source.TYPE_SPLUNK: TCPSourceBuilder,
    source.TYPE_DIRECTORY: DirectorySourceBuilder,
    source.TYPE_SAGE: SageSourceBuilder,
}


def get_builder(source_name: str, source_type: str) -> Builder:
    if source_type not in source.types:
        raise ValueError(f'{source_type} isn\'t supported')
    return types[source_type](source.manager.create_source_obj(source_name, source_type))
