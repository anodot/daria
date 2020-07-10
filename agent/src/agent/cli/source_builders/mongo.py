import click
import re

from .abstract_builder import Builder, SourceException
from agent.tools import infinite_retry, print_json, if_validation_enabled
from pymongo import MongoClient
from agent import source


class MongoSource(Builder):
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

    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_auth(default_config)
        self.prompt_db(default_config)
        self.prompt_collection(default_config)
        self.prompt_offset(default_config)
        self.source.config[self.CONFIG_BATCH_SIZE] = \
            click.prompt('Batch size', type=click.IntRange(1), default=default_config.get(self.CONFIG_BATCH_SIZE, 1000))
        self.prompt_batch_wait_time(default_config)
        self.source.set_config(self.source.config)
        return self.source

    def validate(self):
        source.validator.validate_json(self.source)
        self.validate_connection()
        self.validate_db()
        self.validate_collection()

    def get_mongo_client(self) -> MongoClient:
        args = {}
        if self.source.config.get(self.CONFIG_USERNAME):
            args['authSource'] = self.source.config.get(self.CONFIG_AUTH_SOURCE)
            args['username'] = self.source.config.get(self.CONFIG_USERNAME)
            args['password'] = self.source.config.get(self.CONFIG_PASSWORD)
        return MongoClient(self.source.config[self.CONFIG_CONNECTION_STRING], **args)

    @if_validation_enabled
    def validate_connection(self):
        client = self.get_mongo_client()
        client.server_info()
        click.echo('Connected to Mongo server')

    @infinite_retry
    def prompt_connection(self, default_config: dict):
        self.source.config[self.CONFIG_CONNECTION_STRING] = \
            click.prompt('Connection string', type=click.STRING,
                         default=default_config.get(self.CONFIG_CONNECTION_STRING)).strip()
        self.validate_connection()

    @infinite_retry
    def prompt_auth(self, default_config: dict):
        self.source.config[self.CONFIG_USERNAME] = \
            click.prompt('Username', type=click.STRING, default=default_config.get(self.CONFIG_USERNAME, '')).strip()
        if self.source.config[self.CONFIG_USERNAME] == '':
            return

        self.source.config[self.CONFIG_PASSWORD] = click.prompt('Password', type=click.STRING,
                                                                default=default_config.get(self.CONFIG_PASSWORD, ''))
        self.source.config[self.CONFIG_AUTH_SOURCE] = click.prompt('Authentication Source', type=click.STRING,
                                                                   default=default_config.get(self.CONFIG_AUTH_SOURCE,
                                                                                              '')).strip()
        self.validate_connection()

    def prompt_batch_wait_time(self, default_config: dict):
        default_batch_wait_time = default_config.get(self.CONFIG_MAX_BATCH_WAIT_TIME)
        if default_batch_wait_time:
            default_batch_wait_time = int(re.findall(r'\d+', default_batch_wait_time)[0])
        else:
            default_batch_wait_time = 5
        batch_wait_time = click.prompt('Max batch wait time (seconds)', type=click.IntRange(1),
                                       default=default_batch_wait_time)
        self.source.config[self.CONFIG_MAX_BATCH_WAIT_TIME] = '${' + str(batch_wait_time) + ' * SECONDS}'

    def prompt_offset(self, default_config: dict):
        self.source.config[self.CONFIG_OFFSET_TYPE] = \
            click.prompt('Offset type', type=click.Choice(self.offset_types),
                         default=default_config.get(self.CONFIG_OFFSET_TYPE, self.OFFSET_TYPE_OBJECT_ID))
        default_offset = None if self.source.config[self.CONFIG_OFFSET_TYPE] == self.OFFSET_TYPE_STRING else '3'
        self.source.config[self.CONFIG_INITIAL_OFFSET] = click.prompt(
            'Initial offset (amount of days ago or specific date)', type=click.STRING,
            default=default_config.get(self.CONFIG_INITIAL_OFFSET, default_offset))
        self.source.config[self.CONFIG_OFFSET_FIELD] = \
            click.prompt('Offset field', type=click.STRING,
                         default=default_config.get(self.CONFIG_OFFSET_FIELD, '_id')).strip()

    @if_validation_enabled
    def validate_db(self):
        client = self.get_mongo_client()
        if self.source.config[self.CONFIG_DATABASE] not in client.list_database_names():
            raise SourceException(f'Database {self.source.config[self.CONFIG_DATABASE]} doesn\'t exist')

    @infinite_retry
    def prompt_db(self, default_config):
        self.source.config[self.CONFIG_DATABASE] = \
            click.prompt('Database', type=click.STRING, default=default_config.get(self.CONFIG_DATABASE)).strip()
        self.validate_db()

    @if_validation_enabled
    def validate_collection(self):
        client = self.get_mongo_client()
        if self.source.config[self.CONFIG_COLLECTION] \
                not in client[self.source.config[self.CONFIG_DATABASE]].list_collection_names():
            raise SourceException(f'Collection {self.source.config[self.CONFIG_DATABASE]} doesn\'t exist')

    def get_collection(self):
        client = self.get_mongo_client()
        self.validate_collection()
        return client[self.source.config[self.CONFIG_DATABASE]][self.source.config[self.CONFIG_COLLECTION]]

    @infinite_retry
    def prompt_collection(self, default_config):
        self.source.config[self.CONFIG_COLLECTION] = \
            click.prompt('Collection', type=click.STRING, default=default_config.get(self.CONFIG_COLLECTION)).strip()
        self.source.config[self.CONFIG_IS_CAPPED] = 'capped' in self.get_collection().options()

    # todo refactor
    def set_config(self, config):
        super().set_config(config)
        if self.source.config[self.CONFIG_USERNAME] != '':
            self.source.config[self.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_USER_PASS
        else:
            self.source.config[self.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_NONE
            del self.source.config[self.CONFIG_USERNAME]

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return
        print_json(records)
