from agent import source
from .directory import DirectorySource
from .elastic import ElasticSource
from .influx import InfluxSource
from .jdbc import JDBCSource
from .kafka import KafkaSource
from .mongo import MongoSource
from .sage import SageSource
from .tcp import TCPSource
from .abstract_builder import Builder

types = {
    source.TYPE_INFLUX: InfluxSource,
    source.TYPE_KAFKA: KafkaSource,
    source.TYPE_MONGO: MongoSource,
    source.TYPE_MYSQL: JDBCSource,
    source.TYPE_POSTGRES: JDBCSource,
    source.TYPE_ELASTIC: ElasticSource,
    source.TYPE_SPLUNK: TCPSource,
    source.TYPE_DIRECTORY: DirectorySource,
    source.TYPE_SAGE: SageSource,
}


def get_builder(source_obj: source.source.Source) -> Builder:
    if source_obj.type not in types:
        raise ValueError(f'{source_obj.type} isn\'t supported')
    return types[source_obj.type](source_obj.name, source_obj.type)
