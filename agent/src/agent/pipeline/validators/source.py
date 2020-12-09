from agent import pipeline, streamsets
from agent.source import Source
from agent.source.validator import IConnectionValidator, ValidationException


class SourceConnectionValidator(IConnectionValidator):
    @staticmethod
    def validate(source_: Source):
        test_pipeline = pipeline.manager.build_test_pipeline(source_)
        try:
            streamsets.manager.create(test_pipeline)
            validate_status = streamsets.manager.validate(test_pipeline)
            streamsets.manager.wait_for_preview(test_pipeline, validate_status['previewerId'])
        except streamsets.ApiClientException as e:
            raise ValidationException(str(e))
        finally:
            streamsets.manager.delete(test_pipeline)
        return True
