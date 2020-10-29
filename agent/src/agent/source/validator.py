import json
import os
import jsonschema
import requests
import sqlalchemy

from datetime import datetime
from urllib.parse import urlparse, urlunparse
from agent import source, pipeline
from agent.pipeline.streamsets import StreamSetsApiClient
from agent.modules.tools import if_validation_enabled
from agent.modules import validator
from agent.pipeline import streamsets


class ValidationException(Exception):
    pass


class Validator:
    VALIDATION_SCHEMA_FILE = ''

    def __init__(self, source_: source.Source):
        self.source = source_

    def validate(self):
        self.validate_json()
        self.validate_connection()

    def validate_json(self):
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'json_schema_definitions', self.VALIDATION_SCHEMA_FILE
        )
        with open(file_path) as f:
            json_schema = json.load(f)
        jsonschema.validate(self.source.config, json_schema)

    @if_validation_enabled
    def validate_connection(self):
        streamsets_api_client = StreamSetsApiClient(streamsets.repository.get_any())
        test_pipeline_name = pipeline.manager\
            .create_test_pipeline(pipeline.manager.build_test_pipeline(self.source), streamsets_api_client)
        try:
            validate_status = streamsets_api_client.validate(test_pipeline_name)
            streamsets_api_client.wait_for_preview(test_pipeline_name, validate_status['previewerId'])
        finally:
            streamsets_api_client.delete_pipeline(test_pipeline_name)
        return True


def validate(source_: source.Source):
    get_validator(source_).validate()


def get_validator(source_: source.Source) -> Validator:
    types = {
        source.TYPE_INFLUX: InfluxValidator,
        source.TYPE_KAFKA: KafkaValidator,
        source.TYPE_MONGO: MongoValidator,
        source.TYPE_MYSQL: JDBCValidator,
        source.TYPE_POSTGRES: JDBCValidator,
        source.TYPE_ELASTIC: ElasticValidator,
        source.TYPE_SPLUNK: SplunkValidator,
        source.TYPE_DIRECTORY: DirectoryValidator,
        source.TYPE_SAGE: SageValidator,
        source.TYPE_MONITORING: MonitoringValidator,
        source.TYPE_VICTORIA: VictoriaMetricsValidator,
    }
    return types[source_.type](source_)


class InfluxValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'influx.json'

    def validate(self):
        self.validate_json()
        self.validate_connection()
        self.validate_db()
        self.validate_offset()

    @if_validation_enabled
    def validate_connection(self):
        if not validator.is_valid_url(self.source.config['host']):
            raise ValidationException(
                f"{self.source.config['host']} - wrong url format. Correct format is `scheme://host:port`"
            )
        client = source.db.get_influx_client(self.source.config['host'])
        client.ping()

    @if_validation_enabled
    def validate_db(self):
        client = source.db.get_influx_client(self.source.config['host'], self.source.config.get('username'),
                                             self.source.config.get('password'))
        if not any([db['name'] == self.source.config['db'] for db in client.get_list_database()]):
            raise ValidationException(
                f"Database {self.source.config['db']} not found. Please check your credentials again"
            )

    def validate_offset(self):
        if not self.source.config.get('offset'):
            return

        if self.source.config['offset'].isdigit():
            try:
                int(self.source.config['offset'])
            except ValueError:
                raise ValidationException(self.source.config['offset'] + ' is not a valid integer')
        else:
            try:
                datetime.strptime(self.source.config['offset'], '%d/%m/%Y %H:%M').timestamp()
            except ValueError as e:
                raise ValidationException(str(e))


class ElasticValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'elastic.json'

    @if_validation_enabled
    def validate_connection(self):
        # todo
        self.source.config[source.ElasticSource.CONFIG_IS_INCREMENTAL] = False
        super().validate_connection()


class JDBCValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'jdbc.json'

    def validate(self):
        self.validate_json()
        self.validate_connection_string()
        self.validate_connection()

    @if_validation_enabled
    def validate_connection(self):
        eng = sqlalchemy.create_engine(self._get_connection_url())
        eng.connect()

    def _get_connection_url(self):
        conn_info = urlparse(self.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING])
        if self.source.config.get(source.JDBCSource.CONFIG_PASSWORD):
            userpass = self.source.config[source.JDBCSource.CONFIG_USERNAME] + ':' + self.source.config[
                source.JDBCSource.CONFIG_PASSWORD]
            netloc = userpass + '@' + conn_info.netloc
        else:
            netloc = conn_info.netloc
        scheme = conn_info.scheme + '+mysqlconnector' if self.source.type == 'mysql' else conn_info.scheme
        return urlunparse((scheme, netloc, conn_info.path, '', '', ''))

    @if_validation_enabled
    def validate_connection_string(self):
        if not validator.is_valid_url(self.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING]):
            raise ValidationException('Wrong url format. Correct format is `scheme://host:port`')
        result = urlparse(self.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING])
        if self.source.type == 'mysql' and result.scheme != 'mysql':
            raise ValidationException('Wrong url scheme. Use `mysql`')
        if self.source.type == 'postgres' and result.scheme != 'postgresql':
            raise ValidationException('Wrong url scheme. Use `postgresql`')


class MongoValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'mongo.json'

    def validate(self):
        self.validate_json()
        self.validate_connection()
        self.validate_db()
        self.validate_collection()

    @if_validation_enabled
    def validate_connection(self):
        client = source.db.get_mongo_client(
            self.source.config[source.MongoSource.CONFIG_CONNECTION_STRING],
            self.source.config.get(source.MongoSource.CONFIG_USERNAME),
            self.source.config.get(source.MongoSource.CONFIG_PASSWORD),
            self.source.config.get(source.MongoSource.CONFIG_AUTH_SOURCE)
        )
        client.server_info()

    @if_validation_enabled
    def validate_db(self):
        client = source.db.get_mongo_client(
            self.source.config[source.MongoSource.CONFIG_CONNECTION_STRING],
            self.source.config.get(source.MongoSource.CONFIG_USERNAME),
            self.source.config.get(source.MongoSource.CONFIG_PASSWORD),
            self.source.config.get(source.MongoSource.CONFIG_AUTH_SOURCE)
        )
        if self.source.config[source.MongoSource.CONFIG_DATABASE] not in client.list_database_names():
            raise ValidationException(
                f'Database {self.source.config[source.MongoSource.CONFIG_DATABASE]} doesn\'t exist')

    @if_validation_enabled
    def validate_collection(self):
        client = source.db.get_mongo_client(
            self.source.config[source.MongoSource.CONFIG_CONNECTION_STRING],
            self.source.config.get(source.MongoSource.CONFIG_USERNAME),
            self.source.config.get(source.MongoSource.CONFIG_PASSWORD),
            self.source.config.get(source.MongoSource.CONFIG_AUTH_SOURCE)
        )
        if self.source.config[source.MongoSource.CONFIG_COLLECTION] \
                not in client[self.source.config[source.MongoSource.CONFIG_DATABASE]].list_collection_names():
            raise ValidationException(
                f'Collection {self.source.config[source.MongoSource.CONFIG_DATABASE]} doesn\'t exist')


class SageValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'sage.json'

    def validate(self):
        self.validate_json()
        self.validate_url()
        self.validate_token()

    @if_validation_enabled
    def validate_url(self):
        if not validator.is_valid_url(self.source.config[source.SageSource.URL]):
            raise ValidationException('Wrong url format. Correct format is `scheme://host:port`')
        # TODO: check simple request

    @if_validation_enabled
    def validate_token(self):
        # TODO: check token
        pass


class VictoriaMetricsValidator(Validator):
    VALIDATION_SCHEMA_FILE = 'victoria.json'

    def validate_connection(self):
        url = self.source.config['url'] + '/api/v1/export?match[]={__name__="not_existing_dsger43"}'
        session = requests.Session()
        if self.source.config.get(source.VictoriaMetricsSource.USERNAME):
            session.auth = (
                self.source.config[source.VictoriaMetricsSource.USERNAME],
                self.source.config[source.VictoriaMetricsSource.PASSWORD]
            )
        try:
            res = session.get(url, verify=False)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValidationException(
                'Failed connecting to VictoriaMetrics. Make sure you provided correct url, username and password\n'
                + str(e)
            )


class SchemalessValidator(Validator):
    def validate(self):
        super().validate()
        self.validate_grok_file()

    def validate_grok_file(self):
        if self.source.config.get(source.SchemalessSource.CONFIG_GROK_PATTERN_FILE) and not os.path.isfile(
                self.source.config[source.SchemalessSource.CONFIG_GROK_PATTERN_FILE]):
            raise ValidationException('File does not exist')


class KafkaValidator(SchemalessValidator):
    VALIDATION_SCHEMA_FILE = 'kafka.json'


class SplunkValidator(SchemalessValidator):
    VALIDATION_SCHEMA_FILE = 'tcp_server.json'


class DirectoryValidator(SchemalessValidator):
    VALIDATION_SCHEMA_FILE = 'directory.json'


class MonitoringValidator(Validator):
    def validate(self):
        pass

    def validate_json(self):
        pass

    def validate_connection(self):
        pass
