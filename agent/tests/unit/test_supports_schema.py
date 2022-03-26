from agent import pipeline
from agent import source
from agent.destination import DummyHttpDestination
from agent.pipeline import Pipeline
from agent.source import Source


class Object(object):
    pass


def test_supports_schema():
    for source_type in source.types:
        source_ = Object()
        source_.type = source_type

        pipeline_ = Object()
        pipeline_.source = source_

        pipeline.manager.supports_schema(pipeline_)
