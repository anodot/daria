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
    with open(os.path.join(data_dir, 'destination.json')) as f:
        if destination.repository.exists():
            print('Destination already exists, skipping')
            return
        data = json.load(f)
        dest = destination.HttpDestination()
        dest.config = data['config']
        dest.host_id = data['host_id']
        dest.access_key = data['access_key']
        destination.repository.create(dest)
        print('Destination successfully migrated')


def migrate_sources(data_dir):
    if not source.repository.exists(MONITORING_SOURCE_NAME):
        source.repository.create(source.Source(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {}))
        print('Created monitoring source')
    else:
        print('Monitoring source already exists')
    for root, _, filenames in os.walk(os.path.join(data_dir, 'sources')):
        for filename in filenames:
            if not filename.endswith('.json'):
                print(f'Skipping {filename}')
            with open(os.path.join(root, filename)) as f:
                data = json.load(f)
                if source.repository.exists(data['name']):
                    print(f'Source {data["name"]} already exists, skipping')
                    continue
                source_ = source.Source(data['name'], data['type'], data['config'])
                source.repository.create(source_)
                print(f'Source {data["name"]} successfully migrated')


def migrate_pipelines(data_dir):
    for root, _, filenames in os.walk(os.path.join(data_dir, 'pipelines')):
        for filename in filenames:
            if not filename.endswith('.json'):
                print(f'Skipping {filename}')
            with open(os.path.join(root, filename)) as f:
                data = json.load(f)
                pipeline_id = data.pop('pipeline_id')
                if pipeline.repository.exists(pipeline_id):
                    print(f'Pipeline {pipeline_id} already exists, skipping')
                    continue
                pipeline_ = pipeline.manager.create_object(pipeline_id, data['source']['name'])
                data.pop('source')
                pipeline_.config = data
                pipeline.repository.create(pipeline_)
                print(f'Pipeline {pipeline_id} successfully migrated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate destination, sources and pipelines from files to postgres')
    parser.add_argument('--data_dir', default='/usr/src/app/data', help='Directory where destination, sources and pipelines stored')

    args = parser.parse_args()
    try:
        run(args.data_dir)
    except Exception:
        logger_.exception('Uncaught exception')
