import argparse
import json
import logging
import os
import sys

from agent import logger
from agent import source, pipeline, destination
from agent.constants import MONITORING_SOURCE_NAME

logger_ = logger.get_logger('scripts.migrate-to-db.run')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_.addHandler(handler)


def run(data_dir):
    migrate_destination(data_dir)
    migrate_sources(data_dir)
    migrate_pipelines(data_dir)


def migrate_destination(data_dir):
    dest_path = os.path.join(data_dir, 'destination.json')
    if not os.path.isfile(dest_path):
        raise Exception('Destination does not exist, cannot migrate')
    with open(dest_path) as f:
        if destination.repository.exists():
            logger_.info('Destination already exists, skipping')
            return
        data = json.load(f)
        dest = destination.HttpDestination()
        dest.config = data['config']
        dest.host_id = data['host_id']
        dest.access_key = data.get('access_key', '')
        destination.repository.save(dest)
        logger_.info('Destination successfully migrated')


def migrate_sources(data_dir):
    if not source.repository.exists(MONITORING_SOURCE_NAME):
        source.repository.save(source.Source(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {}))
        logger_.info('Created monitoring source')
    else:
        logger_.info('Monitoring source already exists')
    try:
        for filename in os.listdir(os.path.join(data_dir, 'sources')):
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
            with open(os.path.join(data_dir, filename)) as f:
                data = json.load(f)
                if source.repository.exists(data['name']):
                    logger_.info(f'Source {data["name"]} already exists, skipping')
                    continue
                source_ = source.Source(data['name'], data['type'], data['config'])
                source.repository.save(source_)
                logger_.info(f'Source {data["name"]} successfully migrated')
    except Exception:
        logger_.exception('Uncaught exception')


def migrate_pipelines(data_dir):
    try:
        for filename in os.listdir(os.path.join(data_dir, 'pipelines')):
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
            with open(os.path.join(data_dir, filename)) as f:
                data = json.load(f)
                pipeline_id = data.pop('pipeline_id')
                if pipeline.repository.exists(pipeline_id):
                    logger_.info(f'Pipeline {pipeline_id} already exists, skipping')
                    continue
                pipeline_ = pipeline.manager.create_object(pipeline_id, data['source']['name'])
                data.pop('source')
                pipeline_.config = data
                pipeline.repository.save(pipeline_)
                logger_.info(f'Pipeline {pipeline_id} successfully migrated')
    except Exception:
        logger_.exception('Uncaught exception')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate destination, sources and pipelines from files to postgres')
    parser.add_argument('--data_dir', default='/usr/src/app/data', help='Directory where destination, sources and pipelines stored')
    run(parser.parse_args().data_dir)
