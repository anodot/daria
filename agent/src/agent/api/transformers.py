from typing import Callable
from agent import source


def transform(data: dict) -> dict:
    return {'name': data.pop('name'), 'type': data.pop('type'), 'config': data}


def transform_kafka(data: dict) -> dict:
    conf = {'name': data['name'], 'type': data['type'], 'config': {}}
    if 'broker_uri' in data:
        conf['config']['conf.brokerURI'] = data['broker_uri']
    if 'topics' in data:
        conf['config']['conf.topicList'] = data['topics']
    if 'version' in data:
        conf['config']['version'] = data['version']
    if 'data_format' in data:
        conf['config']['conf.dataFormat'] = data['data_format']
    if 'num_of_threads' in data:
        conf['config']['conf.numberOfThreads'] = data['num_of_threads']
    if 'initial_offset' in data:
        conf['config']['conf.kafkaAutoOffsetReset'] = data['initial_offset']
    if 'max_batch_size' in data:
        conf['config']['conf.maxBatchSize'] = data['max_batch_size']
    if 'batch_wait_time' in data:
        conf['config']['conf.batchWaitTime'] = data['batch_wait_time']
    if 'configuration' in data:
        configuration = []
        for items in data['configuration'].split(','):
            items = items.strip().split(':')
            configuration.append({
                "key": items[0],
                "value": items[1],
            })
        conf['config']['conf.kafkaOptions'] = configuration
    return conf


mapping = {
    source.TYPE_KAFKA: transform_kafka,
}


def get_transformer(source_type: str) -> Callable:
    if source_type not in source.types:
        raise Exception('Wrong source type provided')
    if source_type not in mapping:
        return transform
    return mapping[source_type]
