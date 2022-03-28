import unittest
from unittest.mock import Mock
from agent import pipeline
from agent import source
from agent.pipeline import RawPipeline, TestPipeline


class TestPipelineSupportsSchema(unittest.TestCase):
    def test_supports_schema(self):
        for source_type in source.types:
            source_ = Mock()
            source_.type = source_type

            pipeline_ = Mock()
            pipeline_.source = source_

            pipeline.manager.supports_schema(pipeline_)

    def test_supports_schema_exc(self):
        with self.assertRaises(KeyError):
            source_ = Mock()
            source_.type = 'non_existing_type'
            pipeline_ = Mock()
            pipeline_.source = source_
            pipeline.manager.supports_schema(pipeline_)

    def test_supports_schema_TestPipeline(self):
        source_ = Mock()
        source_.type = 'some_type'
        pipeline_ = Mock(spec=TestPipeline)
        pipeline_.source = source_
        self.assertFalse(pipeline.manager.supports_schema(pipeline_))

    def test_supports_schema_RawPipeline(self):
        source_ = Mock()
        source_.type = 'some_type'
        pipeline_ = Mock(spec=RawPipeline)
        pipeline_.source = source_
        self.assertFalse(pipeline.manager.supports_schema(pipeline_))
