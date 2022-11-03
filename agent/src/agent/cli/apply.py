import click
import json
import os

from agent import cli, pipeline, source
from agent.modules import logger

logger_ = logger.get_logger(__name__, stdout=True)

FAIL = '\033[91m'
ENDC = '\033[0m'


@click.command()
@click.option('-d', '--work-dir', type=click.Path(exists=True), required=True)
@click.option('--keep-not-existing/--remove-not-existing', default=True)
def apply(work_dir, keep_not_existing):
    logger_.info('Run in ' + work_dir)
    sources_dir = os.path.join(work_dir, 'sources')
    pipelines_dir = os.path.join(work_dir, 'pipelines')

    process(sources_dir, populate_source_from_file)
    process(pipelines_dir, populate_pipeline_from_file)

    if not keep_not_existing:
        delete_not_existing(pipelines_dir, pipeline, 'Pipeline')
        delete_not_existing(sources_dir, source, 'Source')


def populate_source_from_file(file):
    cli.source.check_prerequisites()
    exceptions = []
    for config in source.json_builder.extract_configs(file):
        try:
            if 'name' not in config:
                raise Exception(f'Source configs must contain a `name` field, check {file.name}')
            if source.repository.exists(config['name']):
                source.json_builder.edit(config)
            else:
                source.json_builder.build(config)
        except Exception as e:
            exceptions.append(str(e))
    if exceptions:
        raise Exception(json.dumps(exceptions))


def populate_pipeline_from_file(file):
    cli.pipeline.check_prerequisites()
    exceptions = []
    for config in pipeline.json_builder.extract_configs(file):
        try:
            if 'pipeline_id' not in config:
                raise Exception(f'Pipeline configs must contain a `pipeline_id` field, check {file.name}')
            if config.get('transform'):
                with open(config['transform']['file'], 'w+') as f:
                    f.write(config['transform']['config'])
            if pipeline.repository.exists(config['pipeline_id']):
                pipeline.json_builder.edit(config)
            else:
                pipeline.manager.start(pipeline.json_builder.build(config))
        except Exception as e:
            exceptions.append(str(e))
    if exceptions:
        raise Exception(json.dumps(exceptions))


def process(directory, create):
    failed = False
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
                continue
            file_path = os.path.join(root, filename)
            try:
                logger_.info(f'Processing {file_path}')
                with open(file_path) as file:
                    create(file)
                logger_.info('Success')
            except Exception as e:
                logger_.exception(f'{FAIL}EXCEPTION: {type(e).__name__}: {e}\n{ENDC}')
                failed = True
                continue
    if failed:
        exit(1)


def delete_not_existing(directory, module, type_):
    logger_.info('Looking for removed pipelines')
    all_names = _extract_all_names(directory, module, type_)
    for obj in module.repository.get_all():
        if obj.name not in all_names:
            logger_.info(f'{type_} {obj.name} not found in configs, deleting')
            module.manager.delete(obj)
            logger_.info('Success')
    logger_.info('Done')


def _extract_all_names(directory, module, type_):
    names = []
    name_key = 'pipeline_id' if type_ == 'Pipeline' else 'name'
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.json'):
                continue
            with open(os.path.join(root, filename)) as file:
                for config in module.json_builder.extract_configs(file):
                    if name_key not in config:
                        raise Exception(f'{type_} config must contain a `{name_key}`, check {file.name}')
                    names.append(config[name_key])
    return names
