import agent

from .source import *
from . import repository
from . import manager
from . import validator
from . import db
from . import json_builder
from . import sensitive_data

TYPE_CACTI = 'cacti'
TYPE_CLICKHOUSE = 'clickhouse'
TYPE_DIRECTORY = 'directory'
TYPE_DATABRICKS = 'databricks'
TYPE_ELASTIC = 'elastic'
TYPE_INFLUX = 'influx'
TYPE_INFLUX_2 = 'influx2'
TYPE_KAFKA = 'kafka'
TYPE_MONGO = 'mongo'
TYPE_MSSQL = 'mssql'
TYPE_MYSQL = 'mysql'
TYPE_ORACLE = 'oracle'
TYPE_OBSERVIUM = 'observium'
TYPE_POSTGRES = 'postgres'
TYPE_PROMETHEUS = 'prometheus'
TYPE_RRD = 'rrd'
TYPE_SAGE = 'sage'
TYPE_SNMP = 'snmp'
TYPE_SPLUNK = 'splunk'
TYPE_SOLARWINDS = 'solarwinds'
TYPE_THANOS = 'thanos'
TYPE_TOPOLOGY = 'topology'
TYPE_VICTORIA = 'victoria'
TYPE_ZABBIX = 'zabbix'

types = {
    TYPE_CACTI: CactiSource,
    TYPE_CLICKHOUSE: JDBCSource,
    TYPE_DIRECTORY: DirectorySource,
    TYPE_DATABRICKS: JDBCSource,
    TYPE_ELASTIC: ElasticSource,
    TYPE_INFLUX: InfluxSource,
    TYPE_INFLUX_2: Influx2Source,
    TYPE_KAFKA: KafkaSource,
    TYPE_MONGO: MongoSource,
    TYPE_MSSQL: JDBCSource,
    TYPE_MYSQL: JDBCSource,
    TYPE_OBSERVIUM: ObserviumSource,
    TYPE_ORACLE: JDBCSource,
    TYPE_POSTGRES: JDBCSource,
    TYPE_PROMETHEUS: PromQLSource,
    TYPE_RRD: RRDSource,
    TYPE_SAGE: SageSource,
    TYPE_SNMP: SNMPSource,
    TYPE_SOLARWINDS: SolarWindsSource,
    TYPE_SPLUNK: TCPSource,
    TYPE_THANOS: PromQLSource,
    TYPE_TOPOLOGY: TopologySource,
    TYPE_VICTORIA: PromQLSource,
    TYPE_ZABBIX: ZabbixSource,
}

json_schema = {
    'type': 'object',
    'properties': {
        'type': {
            'type': 'string',
            'enum': list(types.keys())
        },
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': 100
        },
        'config': {
            'type': 'object'
        }
    },
    'required': ['type', 'name', 'config']
}


def check_prerequisites() -> list:
    errors = []
    if e := agent.check_streamsets():
        errors.append(e)
    return errors
