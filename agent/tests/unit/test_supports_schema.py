from agent import pipeline
from agent import source
from agent.source import Source


def test_supports_schema():
    for source_type in source.types:
        source_ = Source(f'test_{source_type}', source_type, {})
        pipeline_ = pipeline.manager.build_test_pipeline(source_)
        pipeline.manager.supports_schema(pipeline_)
    assert True
