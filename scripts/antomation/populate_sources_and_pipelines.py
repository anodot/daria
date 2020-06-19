import hashlib
import os
import csv
import shutil

from tempfile import NamedTemporaryFile
from agent.cli import source
from agent.cli import pipeline

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FAIL = '\033[91m'
ENDC = '\033[0m'

SOURCES = os.path.join(ROOT_DIR, 'sources')
PIPELINES = os.path.join(ROOT_DIR, 'pipelines')
SOURCES_CHECKSUMS = os.path.join(ROOT_DIR, 'checksums', 'sources.csv')
PIPELINES_CHECKSUMS = os.path.join(ROOT_DIR, 'checksums', 'pipelines.csv')


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


def process(directory, checksum_file, create, start=None):
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if not should_update(checksum_file, filename, root):
                print(f"Don't need to update {filename}")
                continue
            try:
                with open(file_path) as file:
                    create(file)
                if start:
                    start(['-f', file_path])
            except Exception as e:
                print(f'{FAIL}{e}{ENDC}')
                continue
            update_checksum(checksum_file, filename, root)


process(SOURCES, SOURCES_CHECKSUMS, source.populate_from_file)
process(PIPELINES, PIPELINES_CHECKSUMS, pipeline.populate_from_file, pipeline.start)
