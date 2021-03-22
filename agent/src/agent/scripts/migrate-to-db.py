import argparse
import json
import os

from agent.modules import logger, db
from agent import source, pipeline, destination, streamsets

logger_ = logger.get_logger('scripts.migrate-to-db.run', stdout=True)


def run(data_dir):
    if len(streamsets.repository.get_all()) == 0:
        print(
            'You haven\'t created a streamsets instance in the database, please run `agent streamsets add` first'
        )
        exit(1)
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
    try:
        source_dir = os.path.join(data_dir, 'sources')
        for filename in os.listdir(source_dir):
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
            with open(os.path.join(source_dir, filename)) as f:
                data = json.load(f)
                if source.repository.exists(data['name']):
                    logger_.info(f'Source {data["name"]} already exists, skipping')
                    continue
                source_ = source.Source(data['name'], data['type'], data['config'])
                source.repository.save(source_)
                logger_.info(f'Source {data["name"]} successfully migrated')
    except Exception as e:
        logger_.exception(f'Uncaught exception: {str(e)}')


def migrate_pipelines(data_dir):
    streamsets_ = streamsets.repository.get_all()
    if len(streamsets_) > 1:
        print('You have more than one streamsets instance, currently it\'s possible to migrate only to a single streamsets. You can add more streamsets after migration and then run `agent streamsets balance`')
        exit(1)
    streamsets_ = streamsets_[0]
    try:
        pipeline_dir = os.path.join(data_dir, 'pipelines')
        for filename in os.listdir(pipeline_dir):
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
            with open(os.path.join(pipeline_dir, filename)) as f:
                data = json.load(f)
                pipeline_id = data.pop('pipeline_id')
                if pipeline.repository.exists(pipeline_id):
                    logger_.info(f'Pipeline {pipeline_id} already exists, skipping')
                    continue
                pipeline_ = pipeline.manager.create_object(pipeline_id, data['source']['name'])
                pipeline_.set_streamsets(streamsets_)
                data.pop('source')
                pipeline_.config = data
                # add elastic/sage queries to the config
                if pipeline_.query_file:
                    with open(pipeline_.query_file) as ff:
                        pipeline_.query = ff.read()
                pipeline.repository.save(pipeline_)
                logger_.info(f'Pipeline {pipeline_id} successfully migrated')
    except Exception:
        logger_.exception('Uncaught exception')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate destination, sources and pipelines from files to postgres')
    parser.add_argument('--data_dir', default='/usr/src/app/data', help='Directory where destination, sources and pipelines stored')
    run(parser.parse_args().data_dir)
