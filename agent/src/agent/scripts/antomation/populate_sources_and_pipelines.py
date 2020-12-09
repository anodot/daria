import argparse
import hashlib
import json
import os
import csv
import shutil

from tempfile import NamedTemporaryFile
from agent import pipeline, source, streamsets
from agent.modules import logger, constants, db

logger_ = logger.get_logger('scripts.antomation.run', stdout=True)

FAIL = '\033[91m'
ENDC = '\033[0m'
ANTOMATION_WORKDIR = os.environ.get('ANTOMATION_WORKDIR', os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(ANTOMATION_WORKDIR, 'sources')
PIPELINES_DIR = os.path.join(ANTOMATION_WORKDIR, 'pipelines')
CHECKSUMS_DIR = os.environ.get('CHECKSUMS_DIR', os.path.join(ANTOMATION_WORKDIR, 'checksums'))
SOURCES_CHECKSUMS = os.path.join(CHECKSUMS_DIR, 'sources.csv')
PIPELINES_CHECKSUMS = os.path.join(CHECKSUMS_DIR, 'pipelines.csv')


def populate_source_from_file(file):
    exceptions = []
    for config in source.manager.extract_configs(file):
        try:
            if 'name' not in config:
                raise Exception(f'Source configs must contain a `name` field, check {file.name}')
            if source.repository.exists(config['name']):
                source.manager.edit_source_using_json(config)
            else:
                source.manager.create_source_from_json(config)
        except Exception as e:
            exceptions.append(str(e))
    if exceptions:
        raise Exception(json.dumps(exceptions))


def populate_pipeline_from_file(file):
    exceptions = []
    for config in pipeline.manager.extract_configs(file):
        try:
            if 'pipeline_id' not in config:
                raise Exception(f'Pipeline configs must contain a `pipeline_id` field, check {file.name}')
            if pipeline.repository.exists(config['pipeline_id']):
                pipeline.manager.edit_pipeline_using_json(config)
            else:
                streamsets.manager.start(
                    pipeline.manager.create_pipeline_from_json(config)
                )
        except Exception as e:
            exceptions.append(str(e))
    if exceptions:
        raise Exception(json.dumps(exceptions))


def get_checksum(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        content = file.read()
        file.seek(0)
        for config in json.load(file):
            if 'query_file' in config:
                with open(config['query_file'], 'rb') as f:
                    content += f.read()
        md5_hash.update(content)
    return md5_hash.hexdigest()


def should_update(checksum_file, filename, root):
    with open(checksum_file) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if row[0] == filename:
                return row[1] != get_checksum(os.path.join(root, filename))
    return True


def update_checksum(checksum_file, filename, root):
    file_path = os.path.join(root, filename)
    fields = ['name', 'checksum']
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    updated = False
    with open(checksum_file) as file, tempfile:
        reader = csv.DictReader(file, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)
        for row in reader:
            if row['name'] == filename:
                row['checksum'] = get_checksum(file_path)
                updated = True
            writer.writerow(row)
    shutil.move(tempfile.name, checksum_file)
    if not updated:
        with open(checksum_file, 'a') as file:
            file.write(f'{filename},{get_checksum(file_path)}')


def process(directory, checksum_file, create):
    failed = False
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.json'):
                logger_.info(f'Skipping {filename}')
                continue
            file_path = os.path.join(root, filename)
            if not should_update(checksum_file, filename, root):
                logger_.info(f"Don't need to update {file_path}")
                continue
            try:
                logger_.info(f'Processing {file_path}')
                with open(file_path) as file:
                    create(file)
                logger_.info('Success')
            except Exception as e:
                logger_.exception(f'{FAIL}EXCEPTION: {type(e).__name__}: {str(e)}\n{ENDC}')
                failed = True
                continue
            update_checksum(checksum_file, filename, root)
            logger_.info(f'Updated checksum for {file_path}')
    if failed:
        exit(1)


def delete_not_existing(directory, module, type_):
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep-not-existing', action='store_true', help="shows output")
    if not parser.parse_args().keep_not_existing:
        logger_.info('Looking for removed pipelines')
        all_names = _extract_all_names(directory, module, type_)
        for obj in module.repository.get_all():
            if obj.name not in all_names and not is_monitoring(obj):
                logger_.info(f'{type_} {obj.name} not found in configs, deleting')
                module.manager.delete(obj)
                logger_.info('Success')
        logger_.info('Done')


def is_monitoring(obj) -> bool:
    return (isinstance(obj, pipeline.Pipeline) and pipeline.manager.is_monitoring(obj)) or \
           (isinstance(obj, source.Source) and obj.name == constants.MONITORING_SOURCE_NAME)


def _extract_all_names(directory, module, type_):
    names = []
    name_key = 'pipeline_id' if type_ == 'Pipeline' else 'name'
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.json'):
                continue
            with open(os.path.join(root, filename)) as file:
                for config in module.manager.extract_configs(file):
                    if name_key not in config:
                        raise Exception(f'{type_} config must contain a `{name_key}`, check {file.name}')
                    names.append(config[name_key])
    return names


def create_checksums_dir():
    if not os.path.isdir(CHECKSUMS_DIR):
        os.mkdir(CHECKSUMS_DIR)
    if not os.path.exists(SOURCES_CHECKSUMS):
        with open(SOURCES_CHECKSUMS, 'w'):
            pass
    if not os.path.exists(PIPELINES_CHECKSUMS):
        with open(PIPELINES_CHECKSUMS, 'w'):
            pass


create_checksums_dir()


process(SOURCES_DIR, SOURCES_CHECKSUMS, populate_source_from_file)
process(PIPELINES_DIR, PIPELINES_CHECKSUMS, populate_pipeline_from_file)

delete_not_existing(PIPELINES_DIR, pipeline, 'Pipeline')
delete_not_existing(SOURCES_DIR, source, 'Source')

# todo this is temporary
db.session().commit()
db.session().close()
