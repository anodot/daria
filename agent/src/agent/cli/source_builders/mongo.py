import click
import re

from .abstract_builder import Builder
from agent.tools import infinite_retry
from agent import source, tools


class MongoSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_auth(default_config)
        self.prompt_db(default_config)
        self.prompt_collection(default_config)
        self.prompt_offset(default_config)
        self.source.config[source.MongoSource.CONFIG_BATCH_SIZE] = \
            click.prompt('Batch size', type=click.IntRange(1),
                         default=default_config.get(source.MongoSource.CONFIG_BATCH_SIZE, 1000))
        self.prompt_batch_wait_time(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config: dict):
        self.source.config[source.MongoSource.CONFIG_CONNECTION_STRING] = \
            click.prompt('Connection string', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_CONNECTION_STRING)).strip()
        self.validator.validate_connection()
        click.echo('Successfully connected to Mongo server')

    @infinite_retry
    def prompt_auth(self, default_config: dict):
        self.source.config[source.MongoSource.CONFIG_USERNAME] = \
            click.prompt('Username', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_USERNAME, '')).strip()
        if self.source.config[source.MongoSource.CONFIG_USERNAME] == '':
            return
        self.source.config[source.MongoSource.CONFIG_PASSWORD] = \
            click.prompt('Password', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_PASSWORD, ''))
        self.source.config[source.MongoSource.CONFIG_AUTH_SOURCE] = \
            click.prompt('Authentication Source', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_AUTH_SOURCE, '')).strip()
        self.validator.validate_connection()
        print('Successfully connected to the source')

    def prompt_batch_wait_time(self, default_config: dict):
        default_batch_wait_time = default_config.get(source.MongoSource.CONFIG_MAX_BATCH_WAIT_TIME)
        if default_batch_wait_time:
            default_batch_wait_time = int(re.findall(r'\d+', default_batch_wait_time)[0])
        else:
            default_batch_wait_time = 5
        batch_wait_time = click.prompt('Max batch wait time (seconds)', type=click.IntRange(1),
                                       default=default_batch_wait_time)
        self.source.config[source.MongoSource.CONFIG_MAX_BATCH_WAIT_TIME] = '${' + str(batch_wait_time) + ' * SECONDS}'

    def prompt_offset(self, default_config: dict):
        self.source.config[source.MongoSource.CONFIG_OFFSET_TYPE] = \
            click.prompt('Offset type', type=click.Choice(source.MongoSource.offset_types),
                         default=default_config.get(source.MongoSource.CONFIG_OFFSET_TYPE, source.MongoSource.OFFSET_TYPE_OBJECT_ID))
        default_offset = None if self.source.config[
                                     source.MongoSource.CONFIG_OFFSET_TYPE] == source.MongoSource.OFFSET_TYPE_STRING else '3'
        self.source.config[source.MongoSource.CONFIG_INITIAL_OFFSET] = click.prompt(
            'Initial offset (amount of days ago or specific date)', type=click.STRING,
            default=default_config.get(source.MongoSource.CONFIG_INITIAL_OFFSET, default_offset))
        self.source.config[source.MongoSource.CONFIG_OFFSET_FIELD] = \
            click.prompt('Offset field', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_OFFSET_FIELD, '_id')).strip()

    @infinite_retry
    def prompt_db(self, default_config):
        self.source.config[source.MongoSource.CONFIG_DATABASE] = \
            click.prompt('Database', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_DATABASE)).strip()
        try:
            self.validator.validate_db()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    def _get_collection(self):
        try:
            self.validator.validate_collection()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)
        client = source.db.get_mongo_client(
            self.source.config[source.MongoSource.CONFIG_CONNECTION_STRING],
            self.source.config.get(source.MongoSource.CONFIG_USERNAME),
            self.source.config.get(source.MongoSource.CONFIG_PASSWORD),
            self.source.config.get(source.MongoSource.CONFIG_AUTH_SOURCE)
        )
        return client[self.source.config[source.MongoSource.CONFIG_DATABASE]][self.source.config[source.MongoSource.CONFIG_COLLECTION]]

    @infinite_retry
    def prompt_collection(self, default_config):
        self.source.config[source.MongoSource.CONFIG_COLLECTION] = \
            click.prompt('Collection', type=click.STRING,
                         default=default_config.get(source.MongoSource.CONFIG_COLLECTION)).strip()
        self.source.config[source.MongoSource.CONFIG_IS_CAPPED] = 'capped' in self._get_collection().options()
