import time

from urllib.parse import urlparse
from abc import ABC
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from pymongo import MongoClient
from agent import source


def get_influx_client(host, username=None, password=None, db=None) -> InfluxDBClient:
    influx_url_parsed = urlparse(host)
    influx_url = influx_url_parsed.netloc.split(':')
    args = {'host': influx_url[0], 'port': influx_url[1]}
    if username and username != '':
        args['username'] = username
        args['password'] = password
    if influx_url_parsed.scheme == 'https':
        args['ssl'] = True
    if db:
        args['database'] = db
    return InfluxDBClient(**args)


def has_write_access(client: InfluxDBClient):
    try:
        client.write_points([{
            "measurement": "agent_test",
            "time": time.time_ns(),
            "fields": {
                "val": 1.0
            }
        }])
    except InfluxDBClientError as e:
        if e.code == 403:
            return False
    client.drop_measurement('agent_test')
    return True


class Source(ABC):
    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    # todo refactor children
    def set_config(self, config):
        self.config = config


def get_mongo_client(source_: Source) -> MongoClient:
    args = {}
    if source_.config.get(MongoSource.CONFIG_USERNAME):
        args['authSource'] = source_.config.get(MongoSource.CONFIG_AUTH_SOURCE)
        args['username'] = source_.config.get(MongoSource.CONFIG_USERNAME)
        args['password'] = source_.config.get(MongoSource.CONFIG_PASSWORD)
    return MongoClient(source_.config[MongoSource.CONFIG_CONNECTION_STRING], **args)


class ElasticSource(Source):
    CONFIG_INDEX = 'conf.index'
    CONFIG_MAPPING = 'conf.mapping'
    CONFIG_IS_INCREMENTAL = 'conf.isIncrementalMode'
    CONFIG_QUERY_INTERVAL = 'conf.queryInterval'
    CONFIG_OFFSET_FIELD = 'conf.offsetField'
    CONFIG_INITIAL_OFFSET = 'conf.initialOffset'
    CONFIG_QUERY = 'conf.query'
    CONFIG_CURSOR_TIMEOUT = 'conf.cursorTimeout'
    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_HTTP_URIS = 'conf.httpUris'

    def set_config(self, config):
        super().set_config(config)
        if 'query_interval_sec' in self.config:
            self.config[source.ElasticSource.CONFIG_QUERY_INTERVAL] = '${' + str(
                self.config['query_interval_sec']) + ' * SECONDS}'
        self.config[source.ElasticSource.CONFIG_IS_INCREMENTAL] = True


class InfluxSource(Source):
    pass


class JDBCSource(Source):
    def set_config(self, config):
        super().set_config(config)
        self.config['hikariConfigBean.connectionString'] = 'jdbc:' + self.config['connection_string']


class MongoSource(Source):
    CONFIG_CONNECTION_STRING = 'configBean.mongoConfig.connectionString'
    CONFIG_USERNAME = 'configBean.mongoConfig.username'
    CONFIG_PASSWORD = 'configBean.mongoConfig.password'
    CONFIG_AUTH_SOURCE = 'configBean.mongoConfig.authSource'
    CONFIG_AUTH_TYPE = 'configBean.mongoConfig.authenticationType'
    CONFIG_DATABASE = 'configBean.mongoConfig.database'
    CONFIG_COLLECTION = 'configBean.mongoConfig.collection'
    CONFIG_IS_CAPPED = 'configBean.isCapped'
    CONFIG_OFFSET_TYPE = 'configBean.offsetType'
    CONFIG_INITIAL_OFFSET = 'configBean.initialOffset'
    CONFIG_OFFSET_FIELD = 'configBean.offsetField'
    CONFIG_BATCH_SIZE = 'configBean.batchSize'
    CONFIG_MAX_BATCH_WAIT_TIME = 'configBean.maxBatchWaitTime'

    OFFSET_TYPE_OBJECT_ID = 'OBJECTID'
    OFFSET_TYPE_STRING = 'STRING'
    OFFSET_TYPE_DATE = 'DATE'

    AUTH_TYPE_NONE = 'NONE'
    AUTH_TYPE_USER_PASS = 'USER_PASS'

    offset_types = [OFFSET_TYPE_OBJECT_ID, OFFSET_TYPE_STRING, OFFSET_TYPE_DATE]

    def set_config(self, config):
        super().set_config(config)
        if self.config[source.MongoSource.CONFIG_USERNAME] != '':
            self.config[source.MongoSource.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_USER_PASS
        else:
            self.config[source.MongoSource.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_NONE
            del self.config[source.MongoSource.CONFIG_USERNAME]


class SchemalessSource(Source):
    CONFIG_DATA_FORMAT = 'conf.dataFormat'
    CONFIG_CSV_MAPPING = 'csv_mapping'

    DATA_FORMAT_JSON = 'JSON'
    DATA_FORMAT_CSV = 'DELIMITED'
    DATA_FORMAT_AVRO = 'AVRO'
    DATA_FORMAT_LOG = 'LOG'

    CONFIG_CSV_TYPE = 'conf.dataFormatConfig.csvFileFormat'
    CONFIG_CSV_TYPE_DEFAULT = 'CSV'
    CONFIG_CSV_TYPE_CUSTOM = 'CUSTOM'
    csv_types = [CONFIG_CSV_TYPE_DEFAULT, CONFIG_CSV_TYPE_CUSTOM]

    CONFIG_CSV_HEADER_LINE = 'conf.dataFormatConfig.csvHeader'
    CONFIG_CSV_HEADER_LINE_NO_HEADER = 'NO_HEADER'
    CONFIG_CSV_HEADER_LINE_WITH_HEADER = 'WITH_HEADER'

    CONFIG_CSV_CUSTOM_DELIMITER = 'conf.dataFormatConfig.csvCustomDelimiter'

    CONFIG_AVRO_SCHEMA_SOURCE = 'conf.dataFormatConfig.avroSchemaSource'
    CONFIG_AVRO_SCHEMA = 'conf.dataFormatConfig.avroSchema'
    CONFIG_AVRO_SCHEMA_FILE = 'schema_file'
    CONFIG_AVRO_SCHEMA_REGISTRY_URLS = 'conf.dataFormatConfig.schemaRegistryUrls'
    CONFIG_AVRO_SCHEMA_LOOKUP_MODE = 'conf.dataFormatConfig.schemaLookupMode'

    CONFIG_KEY_DESERIALIZER = 'conf.keyDeserializer'
    CONFIG_VALUE_DESERIALIZER = 'conf.keyDeserializer'

    AVRO_SCHEMA_SOURCE_SOURCE = 'SOURCE'
    AVRO_SCHEMA_SOURCE_INLINE = 'INLINE'
    AVRO_SCHEMA_SOURCE_REGISTRY = 'REGISTRY'
    avro_sources = [AVRO_SCHEMA_SOURCE_SOURCE, AVRO_SCHEMA_SOURCE_INLINE, AVRO_SCHEMA_SOURCE_REGISTRY]

    AVRO_LOOKUP_SUBJECT = 'SUBJECT'
    AVRO_LOOKUP_ID = 'ID'
    AVRO_LOOKUP_AUTO = 'AUTO'
    avro_lookup_modes = [AVRO_LOOKUP_SUBJECT, AVRO_LOOKUP_ID, AVRO_LOOKUP_AUTO]

    CONFIG_AVRO_LOOKUP_ID = 'conf.dataFormatConfig.schemaId'
    CONFIG_AVRO_LOOKUP_SUBJECT = 'conf.dataFormatConfig.subject'

    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'conf.batchWaitTime'

    CONFIG_GROK_PATTERN_DEFINITION = 'conf.dataFormatConfig.grokPatternDefinition'
    CONFIG_GROK_PATTERN = 'conf.dataFormatConfig.grokPattern'
    CONFIG_GROK_PATTERN_FILE = 'grok_definition_file'

    data_formats = [DATA_FORMAT_JSON, DATA_FORMAT_CSV, DATA_FORMAT_AVRO, DATA_FORMAT_LOG]


class KafkaSource(SchemalessSource):
    CONFIG_BROKER_LIST = 'conf.brokerURI'
    CONFIG_CONSUMER_GROUP = 'conf.consumerGroup'
    CONFIG_TOPIC_LIST = 'conf.topicList'
    CONFIG_OFFSET_TYPE = 'conf.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'conf.timestampToSearchOffsets'

    CONFIG_CONSUMER_PARAMS = 'conf.kafkaOptions'
    CONFIG_N_THREADS = 'conf.numberOfThreads'
    CONFIG_LIBRARY = 'library'
    CONFIG_VERSION = 'version'

    OFFSET_EARLIEST = 'EARLIEST'
    OFFSET_LATEST = 'LATEST'
    OFFSET_TIMESTAMP = 'TIMESTAMP'

    DEFAULT_KAFKA_VERSION = '2.0+'

    version_libraries = {'0.10': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '0.11': 'streamsets-datacollector-apache-kafka_2_0-lib',
                         '2.0+': 'streamsets-datacollector-apache-kafka_2_0-lib'}

    def set_config(self, config):
        super().set_config(config)
        self.config[source.KafkaSource.CONFIG_LIBRARY] = \
            source.KafkaSource.version_libraries[
                self.config.get(source.KafkaSource.CONFIG_VERSION, source.KafkaSource.DEFAULT_KAFKA_VERSION)]


class DirectorySource(SchemalessSource):
    pass


class SageSource(Source):
    URL = 'url'
    TOKEN = 'token'


class TCPSource(SchemalessSource):
    pass


class MonitoringSource(Source):
    pass


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass


class SourceConfigDeprecated(SourceException):
    pass

