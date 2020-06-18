import os

from agent.cli import source
from agent.cli import pipeline

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCES = os.path.join(ROOT_DIR, 'sources')
PIPELINES = os.path.join(ROOT_DIR, 'pipelines')


def create(directory, create_function):
    for root, _, filenames in os.walk(directory):
        for file in filenames:
            with open(os.path.join(root, file)) as f:
                create_function(f)


def main():
    create(SOURCES, source.populate_from_file)
    create(PIPELINES, pipeline.populate_from_file)


main()
