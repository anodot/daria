from agent import pipeline
from agent import source
from agent.destination import DummyHttpDestination
from agent.pipeline import Pipeline
from agent.source import Source


def test_supports_schema():
    for source_type in source.types:
        source_ = Source(f'test_{source_type}', source_type, {})
        pipeline_ = Pipeline(source_.name, source_, DummyHttpDestination())
        pipeline.manager.supports_schema(pipeline_)
