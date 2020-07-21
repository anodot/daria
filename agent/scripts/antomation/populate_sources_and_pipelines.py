import hashlib
import json
import os
import csv
import shutil

from tempfile import NamedTemporaryFile
from agent import pipeline, source

FAIL = '\033[91m'
ENDC = '\033[0m'
ROOT_DIR = os.environ.get('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT_DIR, 'sources')
PIPELINES = os.path.join(ROOT_DIR, 'pipelines')
SOURCES_CHECKSUMS = os.path.join(
    os.environ.get('CHECKSUMS_DIR', os.path.join(ROOT_DIR, 'checksums')),
    'sources.csv'
)
PIPELINES_CHECKSUMS = os.path.join(
    os.environ.get('CHECKSUMS_DIR', os.path.join(ROOT_DIR, 'checksums')),
    'pipelines.csv'
)


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
                print(f'Skipping {filename}')
                continue
            file_path = os.path.join(root, filename)
            if not should_update(checksum_file, filename, root):
                print(f"Don't need to update {file_path}")
                continue
            try:
                print(f'Processing {file_path}')
                with open(file_path) as file:
                    create(file)
                print('Success')
            except Exception as e:
                print(f'{FAIL}EXCEPTION: {type(e).__name__}: {str(e)}\n{ENDC}')
                failed = True
                continue
            update_checksum(checksum_file, filename, root)
            print(f'Updated checksum for {file_path}')
    if failed:
        exit(1)


process(SOURCES, SOURCES_CHECKSUMS, populate_source_from_file)
process(PIPELINES, PIPELINES_CHECKSUMS, populate_pipeline_from_file)
