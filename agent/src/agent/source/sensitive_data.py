from copy import deepcopy
from typing import List
from agent import source

MASK = '******'


def mask(config: dict) -> dict:
    return _recursive_mask(deepcopy(config), _get_keywords(config['type']))


def _recursive_mask(dict_: dict, keywords: list):
    for k in dict_:
        if isinstance(dict_[k], dict):
            _recursive_mask(dict_[k], keywords)
        if k in keywords:
            dict_[k] = MASK
    return dict_


def _get_keywords(source_type: str) -> List[str]:
    types = {
        source.TYPE_CACTI: ['mysql_connection_string'],
        source.TYPE_CLICKHOUSE: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_DIRECTORY: [],
        source.TYPE_DATABRICKS: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_ELASTIC: [],
        source.TYPE_HTTP: ['username', 'password'],
        source.TYPE_IMPALA: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_INFLUX: ['username', 'password'],
        source.TYPE_INFLUX_2: ['token'],
        source.TYPE_KAFKA: [],
        source.TYPE_MONGO: [
            'configBean.mongoConfig.connectionString', 'configBean.mongoConfig.username',
            'configBean.mongoConfig.password', 'configBean.mongoConfig.authSource'
        ],
        source.TYPE_MSSQL: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_MYSQL: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_OBSERVIUM: ['username', 'password'],
        source.TYPE_ORACLE: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_POSTGRES: ['connection_string', 'hikariConfigBean.username', 'hikariConfigBean.password'],
        source.TYPE_PROMETHEUS: ['username', 'password'],
        source.TYPE_PRTG: ['username', 'password'],
        source.TYPE_RRD: [],
        source.TYPE_SAGE: ['token'],
        source.TYPE_SNMP: [],
        source.TYPE_SOLARWINDS: ['username', 'password'],
        source.TYPE_SPLUNK: [],
        source.TYPE_THANOS: ['username', 'password'],
        source.TYPE_TOPOLOGY: ['username', 'password'],
        source.TYPE_VICTORIA: ['username', 'password'],
        source.TYPE_ZABBIX: ['user', 'password'],
    }
    if source_type not in source.types:
        raise ValueError(f'`{source_type}` source type isn\'t supported')
    return types[source_type]
