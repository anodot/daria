import sdc_client

from agent import pipeline
from agent.source import Source
from agent.source.validator import IConnectionValidator, ValidationException


class SourceConnectionValidator(IConnectionValidator):
    @staticmethod
    def validate(source_: Source):
        test_pipeline = pipeline.manager.build_source_validation_pipeline(source_)
        try:
            sdc_client.create(test_pipeline)
            validate_status = sdc_client.validate(test_pipeline)
            sdc_client.wait_for_preview(test_pipeline, validate_status['previewerId'])
        except sdc_client.StreamsetsException as e:
            raise ValidationException(str(e))
        finally:
            sdc_client.delete(test_pipeline)
        return True
