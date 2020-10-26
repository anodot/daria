from sqlalchemy.dialects.postgresql import TIMESTAMP
from agent import source
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Column, Integer, String, JSON, func
from agent.modules.db import Entity


class Source(Entity):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    config = Column(MutableDict.as_mutable(JSON))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())

    pipelines = relationship('Pipeline', back_populates='source_')

    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None

    # todo refactor
    def __getattr__(self, attr):
        if attr == 'sample_data':
            return []
        raise AttributeError(f'type object {type(self)} has no attribute {attr}')

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    # todo refactor children
    def set_config(self, config):
        self.config = config


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


class JDBCSource(Source):
    CONFIG_CONNECTION_STRING = 'connection_string'
    CONFIG_USE_CREDENTIALS = 'hikariConfigBean.useCredentials'
    CONFIG_USERNAME = 'hikariConfigBean.username'
    CONFIG_PASSWORD = 'hikariConfigBean.password'

    TIMESTAMP_CONDITION = '{TIMESTAMP_CONDITION}'


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


class SchemalessSource:
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


class KafkaSource(Source, SchemalessSource):
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


class SageSource(Source):
    URL = 'url'
    TOKEN = 'token'


class VictoriaMetricsSource(Source):
    URL = 'url'
    USERNAME = 'username'
    PASSWORD = 'password'


class DirectorySource(Source, SchemalessSource):
    pass


class TCPSource(Source, SchemalessSource):
    pass


class MonitoringSource(Source):
    pass


class InfluxSource(Source):
    pass


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass


class SourceConfigDeprecated(SourceException):
    pass
