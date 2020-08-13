from .source import *
from .source import Source
from . import repository
from . import manager
from . import validator
from . import db

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
    TYPE_MONITORING: Source,
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
