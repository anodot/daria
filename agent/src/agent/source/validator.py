import json
import os
import jsonschema
import sqlalchemy

from datetime import datetime
from urllib.parse import urlparse, urlunparse
from agent import source, pipeline
from agent.streamsets_api_client import api_client
from agent.tools import if_validation_enabled
from agent.validator import is_valid_url


class ValidationException(Exception):
    pass


class Validator:
    def __init__(self, source_: source.Source):
        self.source = source_

    def validate(self):
        self.validate_json()
        self.validate_connection()

    def validate_json(self):
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'json_schema_definitions',
            self._get_validation_schema_file()
        )
        with open(file_path) as f:
            json_schema = json.load(f)
        jsonschema.validate(self.source.config, json_schema)

    def _get_validation_schema_file(self) -> str:
        validation_schema_files = {
            source.TYPE_INFLUX: 'influx.json',
            source.TYPE_KAFKA: 'kafka.json',
            source.TYPE_MONGO: 'mongo.json',
            source.TYPE_MYSQL: 'jdbc.json',
            source.TYPE_POSTGRES: 'jdbc.json',
            source.TYPE_ELASTIC: 'elastic.json',
            source.TYPE_SPLUNK: 'tcp_server.json',
            source.TYPE_DIRECTORY: 'directory.json',
            source.TYPE_SAGE: 'sage.json',
            source.TYPE_MONITORING: 'Monitoring'
        }
        return validation_schema_files[self.source.type]

    @if_validation_enabled
    def validate_connection(self):
        test_pipeline_name = pipeline.manager.create_test_pipeline(self.source)
        try:
            validate_status = api_client.validate(test_pipeline_name)
            api_client.wait_for_preview(test_pipeline_name, validate_status['previewerId'])
        finally:
            api_client.delete_pipeline(test_pipeline_name)
        return True


def validate(source_: source.Source):
    validator = get_validator(source_)
    validator.validate()


def get_validator(source_: source.Source) -> Validator:
    return types[source_.type](source_)


class InfluxValidator(Validator):
    def validate(self):
        self.validate_json()
        self.validate_connection()
        self.validate_db()
        if 'write_host' in self.source.config:
            self.validate_write_host()
            self.validate_write_db()
            self.validate_write_access()
        self.validate_offset()

    @if_validation_enabled
    def validate_connection(self):
        if not is_valid_url(self.source.config['host']):
            raise ValidationException(
                f"{self.source.config['host']} - wrong url format. Correct format is `scheme://host:port`"
            )
        client = source.get_influx_client(self.source.config['host'])
        client.ping()

    @if_validation_enabled
    def validate_db(self):
        client = source.get_influx_client(self.source.config['host'], self.source.config.get('username'),
                                          self.source.config.get('password'))
        if not any([db['name'] == self.source.config['db'] for db in client.get_list_database()]):
            raise ValidationException(
                f"Database {self.source.config['db']} not found. Please check your credentials again"
            )

    @if_validation_enabled
    def validate_write_host(self):
        if not is_valid_url(self.source.config['write_host']):
            raise ValidationException(
                f"{self.source.config['write_host']} - wrong url format. Correct format is `scheme://host:port`"
            )
        client = source.get_influx_client(self.source.config['write_host'])
        client.ping()

    @if_validation_enabled
    def validate_write_db(self):
        client = source.get_influx_client(self.source.config['write_host'], self.source.config.get('write_username'),
                                          self.source.config.get('write_password'))
        if not any([db['name'] == self.source.config['write_db'] for db in client.get_list_database()]):
            raise ValidationException(
                f"Database {self.source.config['write_db']} not found. Please check your credentials again")

    @if_validation_enabled
    def validate_write_access(self):
        client = source.get_influx_client(self.source.config['write_host'], self.source.config.get('write_username'),
                                          self.source.config.get('write_password'),
                                          self.source.config['write_db'])
        if not source.has_write_access(client):
            raise ValidationException(
                f"""User {self.source.config.get('write_username')} does not have write permissions for db
                 {self.source.config['write_db']} at {self.source.config['write_host']}"""
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
    @if_validation_enabled
    def validate_connection(self):
        # todo
        self.source.config[source.ElasticSource.CONFIG_IS_INCREMENTAL] = False
        super().validate_connection()


class JDBCValidator(Validator):
    def validate(self):
        self.validate_json()
        self.validate_connection_string()
        self.validate_connection()

    @if_validation_enabled
    def validate_connection(self):
        eng = sqlalchemy.create_engine(self._get_connection_url())
        eng.connect()

    def _get_connection_url(self):
        conn_info = urlparse(self.source.config['connection_string'])
        if self.source.config.get('hikariConfigBean.useCredentials'):
            userpass = self.source.config['hikariConfigBean.username'] + ':' + self.source.config[
                'hikariConfigBean.password']
            netloc = userpass + '@' + conn_info.netloc
        else:
            netloc = conn_info.netloc
        scheme = conn_info.scheme + '+mysqlconnector' if self.source.type == 'mysql' else conn_info.scheme
        return urlunparse((scheme, netloc, conn_info.path, '', '', ''))

    @if_validation_enabled
    def validate_connection_string(self):
        if not is_valid_url(self.source.config['connection_string']):
            raise ValidationException('Wrong url format. Correct format is `scheme://host:port`')
        result = urlparse(self.source.config['connection_string'])
        if self.source.type == 'mysql' and result.scheme != 'mysql':
            raise ValidationException('Wrong url scheme. Use `mysql`')
        if self.source.type == 'postgres' and result.scheme != 'postgresql':
            raise ValidationException('Wrong url scheme. Use `postgresql`')


class MongoValidator(Validator):
    def validate(self):
        self.validate_json()
        self.validate_connection()
        self.validate_db()
        self.validate_collection()

    @if_validation_enabled
    def validate_connection(self):
        client = source.get_mongo_client(self.source)
        client.server_info()

    @if_validation_enabled
    def validate_db(self):
        client = source.get_mongo_client(self.source)
        if self.source.config[source.MongoSource.CONFIG_DATABASE] not in client.list_database_names():
            raise ValidationException(f'Database {self.source.config[source.MongoSource.CONFIG_DATABASE]} doesn\'t exist')

    @if_validation_enabled
    def validate_collection(self):
        client = source.get_mongo_client(self.source)
        if self.source.config[source.MongoSource.CONFIG_COLLECTION] \
                not in client[self.source.config[source.MongoSource.CONFIG_DATABASE]].list_collection_names():
            raise ValidationException(f'Collection {self.source.config[source.MongoSource.CONFIG_DATABASE]} doesn\'t exist')


class SageValidator(Validator):
    def validate(self):
        self.validate_json()
        self.validate_url()
        self.validate_token()

    @if_validation_enabled
    def validate_url(self):
        if not is_valid_url(self.source.config[source.SageSource.URL]):
            raise ValidationException('Wrong url format. Correct format is `scheme://host:port`')
        # TODO: check simple request

    @if_validation_enabled
    def validate_token(self):
        # TODO: check token
        pass


class SchemalessValidator(Validator):
    def validate(self):
        super().validate()
        self.validate_grok_file()

    def validate_grok_file(self):
        if self.source.config.get(source.SchemalessSource.CONFIG_GROK_PATTERN_FILE) and not os.path.isfile(
                self.source.config[source.SchemalessSource.CONFIG_GROK_PATTERN_FILE]):
            raise ValidationException('File does not exist')


types = {
    source.TYPE_INFLUX: InfluxValidator,
    source.TYPE_KAFKA: SchemalessValidator,
    source.TYPE_MONGO: MongoValidator,
    source.TYPE_MYSQL: JDBCValidator,
    source.TYPE_POSTGRES: JDBCValidator,
    source.TYPE_ELASTIC: ElasticValidator,
    source.TYPE_SPLUNK: SchemalessValidator,
    source.TYPE_DIRECTORY: SchemalessValidator,
    source.TYPE_SAGE: SageValidator,
}
