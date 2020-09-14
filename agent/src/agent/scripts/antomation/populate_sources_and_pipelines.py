import hashlib
import json
import os
import csv
import shutil
import logging
import sys

from tempfile import NamedTemporaryFile
from agent import pipeline, source
from agent.modules import logger

logger_ = logger.get_logger('scripts.antomation.run')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_.addHandler(handler)

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
                raise Exception('Source config should contain a source name')
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
                raise Exception('Pipeline config should contain a pipeline_id')
            if pipeline.repository.exists(config['pipeline_id']):
                pipeline.manager.edit_pipeline_using_json(config)
            else:
                pipeline_ = pipeline.manager.create_pipeline_from_json(config)
                pipeline.manager.start(pipeline_)
        except Exception as e:
            exceptions.append(str(e))
    if exceptions:
        raise Exception(json.dumps(exceptions))


def get_checksum(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        content = file.read()
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


process(SOURCES_DIR, SOURCES_CHECKSUMS, populate_source_from_file)
process(PIPELINES_DIR, PIPELINES_CHECKSUMS, populate_pipeline_from_file)
