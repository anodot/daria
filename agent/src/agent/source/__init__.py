from .abstract_source import Source, SourceNotExists, SourceException, SourceConfigDeprecated
from .jdbc import JDBCSource
from .influx import InfluxSource
from .kafka import KafkaSource
from .mongo import MongoSource
from .elastic import ElasticSource
from .tcp import TCPSource
from .directory import DirectorySource
from .monitoring import MonitoringSource
from .sage import SageSource
from agent.constants import MONITORING_SOURCE_NAME
from agent.repository import source_repository

TYPE_INFLUX = 'influx'
TYPE_KAFKA = 'kafka'
TYPE_MONGO = 'mongo'
TYPE_MYSQL = 'mysql'
TYPE_POSTGRES = 'postgres'
TYPE_ELASTIC = 'elastic'
TYPE_SPLUNK = 'splunk'
TYPE_DIRECTORY = 'directory'
TYPE_SAGE = 'sage'
TYPE_MONITORING = 'Monitoring'

types = {
    TYPE_INFLUX: InfluxSource,
    TYPE_KAFKA: KafkaSource,
    TYPE_MONGO: MongoSource,
    TYPE_MYSQL: JDBCSource,
    TYPE_POSTGRES: JDBCSource,
    TYPE_ELASTIC: ElasticSource,
    TYPE_SPLUNK: TCPSource,
    TYPE_DIRECTORY: DirectorySource,
    TYPE_SAGE: SageSource,
}

json_schema = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'enum': list(types.keys())},
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
        'config': {'type': 'object'}
    },
    'required': ['type', 'name', 'config']
}
