import click
import re

from .prompt_interface import PromptInterface


class PromptMongo(PromptInterface):

    def prompt(self, default_config, advanced=False):
        config = dict()
        config['configBean.mongoConfig.connectionString'] = click.prompt('Connection string',
                                                                         type=click.STRING,
                                                                         default=default_config.get(
                                                                             'configBean.mongoConfig.connectionString'))
        config['configBean.mongoConfig.username'] = click.prompt('Username',
                                                                 type=click.STRING,
                                                                 default=default_config.get(
                                                                     'configBean.mongoConfig.username', ''))
        config['configBean.mongoConfig.password'] = click.prompt('Password',
                                                                 type=click.STRING,
                                                                 default=default_config.get(
                                                                     'configBean.mongoConfig.password', ''))
        config['configBean.mongoConfig.authSource'] = click.prompt('Authentication Source',
                                                                   type=click.STRING,
                                                                   default=default_config.get(
                                                                       'configBean.mongoConfig.authSource', ''))
        config['configBean.mongoConfig.database'] = click.prompt('Database',
                                                                 type=click.STRING,
                                                                 default=default_config.get(
                                                                     'configBean.mongoConfig.database'))
        config['configBean.mongoConfig.collection'] = click.prompt('Collection',
                                                                   type=click.STRING,
                                                                   default=default_config.get(
                                                                       'configBean.mongoConfig.collection'))
        config['configBean.isCapped'] = click.prompt('Is collection capped',
                                                     type=click.STRING,
                                                     default=default_config.get('configBean.mongoConfig.isCapped',
                                                                                False))
        config['configBean.offsetType'] = click.prompt('Offset type', type=click.Choice(['OBJECTID', 'STRING', 'DATE']),
                                                       default=default_config.get('configBean.offsetType', 'OBJECTID'))

        default_offset = None if config['configBean.offsetType'] == 'STRING' else '3'
        config['configBean.initialOffset'] = click.prompt('Initial offset (amount of days ago or specific date)',
                                                          type=click.STRING,
                                                          default=default_config.get('configBean.initialOffset',
                                                                                     default_offset))

        config['configBean.offsetField'] = click.prompt('Offset field', type=click.STRING,
                                                        default=default_config.get('configBean.offsetField', '_id'))
        config['configBean.batchSize'] = click.prompt('Batch size', type=click.INT,
                                                      default=default_config.get('configBean.batchSize', 1000))

        default_batch_wait_time = default_config.get('configBean.maxBatchWaitTime')
        if default_batch_wait_time:
            default_batch_wait_time = re.findall(r'\d+', default_batch_wait_time)[0]
        else:
            default_batch_wait_time = '5'
        batch_wait_time = click.prompt('Max batch wait time (seconds)', type=click.STRING,
                                       default=default_batch_wait_time)
        config['configBean.maxBatchWaitTime'] = '${' + str(batch_wait_time) + ' * SECONDS}'

        if config['configBean.mongoConfig.username'] == '':
            config['configBean.mongoConfig.authenticationType'] = 'NONE'
        return config
