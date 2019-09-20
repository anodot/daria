import click
import json
import os
import time

from .abstract_source import Source, SourceException
from agent.tools import infinite_retry
from agent.streamsets_api_client import api_client


class KafkaSource(Source):
    CONFIG_BROKER_LIST = 'kafkaConfigBean.metadataBrokerList'
    CONFIG_CONSUMER_GROUP = 'kafkaConfigBean.consumerGroup'
    CONFIG_TOPIC = 'kafkaConfigBean.topic'
    CONFIG_OFFSET_TYPE = 'kafkaConfigBean.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'kafkaConfigBean.timestampToSearchOffsets'
    CONFIG_BATCH_SIZE = 'kafkaConfigBean.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'kafkaConfigBean.maxWaitTime'
    CONFIG_CONSUMER_PARAMS = 'kafkaConfigBean.kafkaConsumerConfigs'

    OFFSET_EARLIEST = 'EARLIEST'
    OFFSET_LATEST = 'LATEST'
    OFFSET_TIMESTAMP = 'TIMESTAMP'

    TEST_PIPELINE_NAME = 'test_kafka'

    def wait_for_preview(self, preview_id, tries=5, initial_delay=2):
        for i in range(1, tries):
            response = api_client.get_preview_status(self.TEST_PIPELINE_NAME, preview_id)
            if response['status'] != 'VALIDATING' and response['status'] != 'CREATED':
                return response
            delay = initial_delay ** i
            if i == tries:
                raise SourceException(f"Can't connect to kafka")
            print(f"Validating connection. Check again after {delay} seconds...")
            time.sleep(delay)

    def validate_connection(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines',
                               self.TEST_PIPELINE_NAME + '.json'), 'r') as f:
            data = json.load(f)

        pipeline_config = data['pipelineConfig']
        new_pipeline = api_client.create_pipeline(self.TEST_PIPELINE_NAME)
        for conf in pipeline_config['stages'][0]['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]
        pipeline_config['uuid'] = new_pipeline['uuid']
        api_client.update_pipeline(self.TEST_PIPELINE_NAME, pipeline_config)

        validate_status = api_client.validate(self.TEST_PIPELINE_NAME)
        self.wait_for_preview(validate_status['previewerId'])
        preview_data = api_client.get_preview_data(self.TEST_PIPELINE_NAME, validate_status['previewerId'])
        if preview_data['status'] == 'INVALID':
            errors = []
            for issue in preview_data['issues']['stageIssues']['KafkaConsumer_01']:
                errors.append(issue['message'])
            api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
            raise SourceException('Connection error. ' + '. '.join(errors))

        api_client.delete_pipeline(self.TEST_PIPELINE_NAME)
        return True

    @infinite_retry
    def prompt_connection(self, default_config, advanced=False):
        self.config[self.CONFIG_BROKER_LIST] = click.prompt('Kafka broker connection string',
                                                            type=click.STRING,
                                                            default=default_config.get(self.CONFIG_BROKER_LIST))
        if advanced:
            self.prompt_consumer_params(default_config)

        self.validate_connection()
        click.echo('Successfully connected to kafka')

    @infinite_retry
    def prompt_consumer_params(self, default_config):
        default_kafka_config = default_config.get(self.CONFIG_CONSUMER_PARAMS, '')
        if default_kafka_config:
            default_kafka_config = ' '.join([i['key'] + ':' + i['value'] for i in default_kafka_config])
        kafka_config = click.prompt('Kafka Configuration', type=click.STRING, default=default_kafka_config)
        self.config[self.CONFIG_CONSUMER_PARAMS] = []
        for i in kafka_config.split(','):
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format')

            self.config[self.CONFIG_CONSUMER_PARAMS].append({'key': pair[0], 'value': pair[1]})

    def prompt(self, default_config, advanced=False):
        self.config = dict()
        self.prompt_connection(default_config, advanced)

        self.config[self.CONFIG_CONSUMER_GROUP] = click.prompt('Consumer group', type=click.STRING,
                                                               default=default_config.get(self.CONFIG_CONSUMER_GROUP,
                                                                                          'anodotAgent'))
        self.config[self.CONFIG_TOPIC] = click.prompt('Topic', type=click.STRING,
                                                      default=default_config.get(self.CONFIG_TOPIC))
        self.config[self.CONFIG_OFFSET_TYPE] = click.prompt('Initial offset',
                                                            type=click.Choice([self.OFFSET_EARLIEST, self.OFFSET_LATEST,
                                                                               self.OFFSET_TIMESTAMP]),
                                                            default=default_config.get(self.CONFIG_OFFSET_TYPE,
                                                                                       self.OFFSET_EARLIEST))
        if self.config[self.CONFIG_OFFSET_TYPE] == self.OFFSET_TIMESTAMP:
            self.config[self.CONFIG_OFFSET_TIMESTAMP] = click.prompt(
                'Offset timestamp (unix timestamp in milliseconds)',
                type=click.STRING,
                default=default_config.get(self.CONFIG_OFFSET_TIMESTAMP))

        if advanced:
            self.config[self.CONFIG_BATCH_SIZE] = click.prompt('Max Batch Size (records)', type=click.INT,
                                                               default=default_config.get(self.CONFIG_BATCH_SIZE, 1000))
            self.config[self.CONFIG_BATCH_WAIT_TIME] = click.prompt('Batch Wait Time (ms)', type=click.INT,
                                                                    default=default_config.get(
                                                                        self.CONFIG_BATCH_WAIT_TIME,
                                                                        1000))

        return self.config
