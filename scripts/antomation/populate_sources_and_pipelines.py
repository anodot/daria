import hashlib
import os
import csv
import shutil

from tempfile import NamedTemporaryFile
from agent import pipeline
from agent.cli.source import extract_configs as extract_source_configs, edit_using_file as edit_source_using_file, \
    create_from_file as create_source_from_file
from agent.cli.pipeline import extract_configs as extract_pipeline_configs, \
    edit_using_file as edit_pipeline_using_file, create_from_file as create_pipeline_from_file, start as start_pipeline
from agent.repository import source_repository, pipeline_repository

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FAIL = '\033[91m'
ENDC = '\033[0m'

SOURCES = os.path.join(ROOT_DIR, 'sources')
PIPELINES = os.path.join(ROOT_DIR, 'pipelines')
SOURCES_CHECKSUMS = os.path.join(ROOT_DIR, 'checksums', 'sources.csv')
PIPELINES_CHECKSUMS = os.path.join(ROOT_DIR, 'checksums', 'pipelines.csv')


def populate_source_from_file(file):
    for config in extract_source_configs(file):
        if 'name' not in config:
            raise Exception('Source config should contain a source name')
        if source_repository.exists(config['name']):
            edit_source_using_file(file)
        else:
            create_source_from_file(file)


def populate_pipeline_from_file(file):
    for config in extract_pipeline_configs(file):
        if 'pipeline_id' not in config:
            raise Exception('Pipeline config should contain a pipeline_id')
        if pipeline_repository.exists(config['pipeline_id']):
            edit_pipeline_using_file(file)
        else:
            create_pipeline_from_file(file)
            start_pipeline(['-f', file.name])


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
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if not should_update(checksum_file, filename, root):
                print(f"Don't need to update {filename}")
                continue
            try:
                with open(file_path) as file:
                    create(file)
            except Exception as e:
                print(f'{FAIL}{e}{ENDC}')
                continue
            update_checksum(checksum_file, filename, root)


process(SOURCES, SOURCES_CHECKSUMS, populate_source_from_file)
process(PIPELINES, PIPELINES_CHECKSUMS, populate_pipeline_from_file)
