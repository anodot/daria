import os

from agent.cli import source
from agent.cli import pipeline

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCES = os.path.join(ROOT_DIR, 'sources')
PIPELINES = os.path.join(ROOT_DIR, 'pipelines')


def process(directory, create, start=None):
    for root, _, filenames in os.walk(directory):
        for file in filenames:
            with open(os.path.join(root, file)) as handle:
                create(handle)
            if start:
                start(['-f', os.path.join(root, file)])


process(SOURCES, source.populate_from_file)
process(PIPELINES, pipeline.populate_from_file, pipeline.start)
